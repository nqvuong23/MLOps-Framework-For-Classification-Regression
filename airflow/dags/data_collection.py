"""
data_collection.py
==================
DAG factory cho tính năng Data Collection: mỗi `problems/<problem_id>/collection.yaml`
sinh ra một DAG `<problem_id>_collect`. Thêm bài toán mới = thêm 1 thư mục config, không sửa file này.

Flow của mỗi DAG:
  1. resolve_window → Tính khoảng điểm neo có nhãn đã "chín":
                      t ∈ [T − H − M − interval, T − H − M), T = logical_date của run
  2. extract        → Gọi API nguồn, lưu NGUYÊN JSON (gzip) vào landing/
  3. flatten        → JSON → bảng quan sát (entity_id, event_time, mỗi biến một cột) → observations/
  4. build_labels   → Tính nhãn trên cửa sổ (t, t + H] → bảng training → labeled/
  5. report         → Ghi manifest, log cảnh báo nếu không có dòng nào được gán nhãn

Không có cleaning / feature engineering ở đây — đó là các khối phía sau.

Chạy cho một khoảng tuỳ chọn (tối đa 31 ngày) bằng cách trigger DAG với conf:
  {"start": "2026-09-01", "end": "2026-09-08"}     # khoảng điểm neo [start, end), UTC
Backfill dài hơn: dùng CLI `python -m framework.collection run --problem <id> --start ... --end ...`.

Dữ liệu ghi tại s3://$S3_BUCKET_NAME/$S3_PREFIX_COLLECTION/<problem_id>/.
"""

import os
import sys
import logging
from datetime import datetime, timedelta, timezone

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

sys.path.insert(0, os.environ.get("FRAMEWORK_ROOT", "/opt/airflow"))
from framework.collection import pipeline
from framework.collection.config import discover_problem_ids, load_config
from framework.collection.window import Window, explicit_window, parse_time, scheduled_window

logger = logging.getLogger(__name__)

# Khoảng điểm neo tối đa cho một run trigger tay — dài hơn thì dùng CLI để chia nhỏ
MAX_MANUAL_RANGE = timedelta(days=31)


# ── Task Functions ─────────────────────────────────────────────────────────────

def resolve_window(problem_id: str, **context):
    """
    Task 1: Xác định cửa sổ thu thập. Chỉ dựa vào logical_date của run (không dùng now())
    để rerun cùng một run cho ra đúng cửa sổ cũ.
    """
    cfg = load_config(problem_id)
    dag_run = context.get("dag_run")
    conf = (dag_run.conf or {}) if dag_run else {}

    if conf.get("start") and conf.get("end"):
        window = explicit_window(cfg, parse_time(conf["start"]), parse_time(conf["end"]))
        if window.anchor_end - window.anchor_start > MAX_MANUAL_RANGE:
            raise ValueError(f"Khoảng điểm neo vượt {MAX_MANUAL_RANGE.days} ngày — dùng CLI để backfill")
    else:
        # Airflow 3: run trigger tay có thể không có logical_date → dùng run_after
        reference = (context.get("logical_date") or context.get("data_interval_end")
                     or getattr(dag_run, "run_after", None) or datetime.now(timezone.utc))
        window = scheduled_window(cfg, reference)

    logger.info(f"[{problem_id}] điểm neo [{window.anchor_start} → {window.anchor_end}) | "
                f"dữ liệu cần đến {window.fetch_end}")
    return window.to_dict()


def _load(problem_id: str, context):
    cfg = load_config(problem_id)
    window = Window.from_dict(context["ti"].xcom_pull(task_ids="resolve_window"))
    return cfg, window, pipeline.get_storage(cfg)


def extract(problem_id: str, **context):
    """Task 2: Gọi API → landing/. XCom chỉ trả số đếm + đường dẫn."""
    cfg, window, storage = _load(problem_id, context)
    return pipeline.extract(cfg, window, storage)


def flatten(problem_id: str, **context):
    """Task 3: landing/ → observations/ (bảng quan sát dạng rộng)."""
    cfg, window, storage = _load(problem_id, context)
    return pipeline.flatten(cfg, window, storage)


def build_labels(problem_id: str, **context):
    """Task 4: observations/ → labeled/ (chỉ giữ dòng có nhãn đã xác định)."""
    cfg, window, storage = _load(problem_id, context)
    return pipeline.label(cfg, window, storage)


def report(problem_id: str, **context):
    """Task 5: Ghi manifest; log cảnh báo khi lần chạy không sinh được dữ liệu training."""
    cfg, window, storage = _load(problem_id, context)
    ti = context["ti"]
    stages = {task_id: ti.xcom_pull(task_ids=task_id) for task_id in ("extract", "flatten", "build_labels")}
    summary = pipeline.report(cfg, window, storage, stages)

    if summary["warnings"]:
        logger.warning(f"[{problem_id}] cửa sổ {window.key}: {'; '.join(summary['warnings'])} | "
                       f"{stages['build_labels'] or {}}")
    return {"window": window.key, **(stages["build_labels"] or {})}


def log_failure(context):
    """on_failure_callback: ghi lỗi của task ra log (chưa gửi alert ra ngoài)."""
    ti = context.get("ti") or context.get("task_instance")
    logger.error(f"[{getattr(ti, 'dag_id', '?')}] task '{getattr(ti, 'task_id', '?')}' thất bại "
                 f"(lần thử {getattr(ti, 'try_number', '?')}): {context.get('exception')!r}")


# ── DAG Factory ───────────────────────────────────────────────────────────────

def build_collection_dag(cfg) -> DAG:
    default_args = {
        "owner": "mlops-team",
        "depends_on_past": False,
        "retries": 2,
        "retry_delay": timedelta(minutes=10),
        "on_failure_callback": log_failure,
    }
    dag = DAG(
        dag_id=f"{cfg.problem_id}_collect",
        description=cfg.description,
        schedule=cfg.schedule,
        start_date=cfg.start_date,
        catchup=False,
        max_active_runs=1,        # các run cùng ghi vào partition theo ngày → không chạy song song
        default_args=default_args,
        tags=["data-collection", cfg.source_type, cfg.task_type],
    )
    kwargs = {"problem_id": cfg.problem_id}
    with dag:
        t1 = PythonOperator(task_id="resolve_window", python_callable=resolve_window, op_kwargs=kwargs)
        t2 = PythonOperator(task_id="extract", python_callable=extract, op_kwargs=kwargs,
                            execution_timeout=timedelta(minutes=30))
        t3 = PythonOperator(task_id="flatten", python_callable=flatten, op_kwargs=kwargs)
        t4 = PythonOperator(task_id="build_labels", python_callable=build_labels, op_kwargs=kwargs)
        t5 = PythonOperator(task_id="report", python_callable=report, op_kwargs=kwargs)

        t1 >> t2 >> t3 >> t4 >> t5
    return dag


# Mỗi bài toán một DAG, đăng ký vào globals() dưới đúng dag_id để Airflow nhận diện
globals().update({
    dag.dag_id: dag
    for dag in (build_collection_dag(load_config(problem_id)) for problem_id in discover_problem_ids())
})
