"""
PostgreSQL (Supabase) integration layer.
Drop-in replacement for snowflake_service.py.
Uses direct Postgres connection via psycopg2.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, Optional
from collections import Counter
from threading import Lock

import psycopg2
from psycopg2.extras import execute_values

from backend.app.core.settings import get_settings

# -----------------------------------------------------------------------------
# Connection handling (lazy, thread-safe)
# -----------------------------------------------------------------------------

_conn = None
_lock = Lock()


def _get_conn():
    global _conn

    if _conn is not None:
        return _conn

    with _lock:
        if _conn is not None:
            return _conn

        settings = get_settings()

        if not all([
            settings.supabase_db_host,
            settings.supabase_db_name,
            settings.supabase_db_user,
            settings.supabase_db_password,
        ]):
            raise RuntimeError("Supabase Postgres DB_* env vars are not fully configured")

        _conn = psycopg2.connect(
            host=settings.supabase_db_host,
            dbname=settings.supabase_db_name,
            user=settings.supabase_db_user,
            password=settings.supabase_db_password,
            port=settings.supabase_db_port or 5432,
        )
        _conn.autocommit = True
        return _conn


# -----------------------------------------------------------------------------
# Compatibility shim
# -----------------------------------------------------------------------------

def init_snowflake():
    return True


# -----------------------------------------------------------------------------
# Write operations
# -----------------------------------------------------------------------------

def store_simulation_run(repo_id: str, run_id: str, summary: Dict[str, Any]) -> bool:
    try:
        conn = _get_conn()
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO simulation_runs (repo_id, run_id, overall_severity, timestamp)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    repo_id,
                    run_id,
                    summary.get("overall_severity", "unknown"),
                    summary.get("timestamp"),
                ),
            )
        return True
    except Exception:
        return False


def store_affected_files(repo_id: str, run_id: str, file_list: Iterable[Any]) -> bool:
    rows = []

    for entry in file_list:
        if isinstance(entry, dict):
            file_path = entry.get("file_path") or entry.get("path")
            if not file_path:
                continue
            rows.append(
                (
                    repo_id,
                    run_id,
                    file_path,
                    entry.get("severity", "unknown"),
                )
            )

    if not rows:
        return True

    try:
        conn = _get_conn()
        with conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO affected_files (repo_id, run_id, file_path, severity)
                VALUES %s
                """,
                rows,
            )
        return True
    except Exception:
        return False


def store_ai_insight(repo_id: str, run_id: str, insight: str) -> bool:
    if not insight:
        return False

    try:
        conn = _get_conn()
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO ai_insights (repo_id, run_id, insight)
                VALUES (%s, %s, %s)
                """,
                (repo_id, run_id, insight),
            )
        return True
    except Exception:
        return False


# -----------------------------------------------------------------------------
# Read helpers
# -----------------------------------------------------------------------------

def _build_report_payload(repo_id: str, run_row: tuple) -> Dict[str, Any]:
    run_id, overall_severity, created_at = run_row


    conn = _get_conn()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT file_path, severity
            FROM affected_files
            WHERE repo_id = %s AND run_id = %s
            """,
            (repo_id, run_id),
        )
        files = cur.fetchall()

        cur.execute(
            """
            SELECT insight
            FROM ai_insights
            WHERE repo_id = %s AND run_id = %s
            LIMIT 1
            """,
            (repo_id, run_id),
        )
        insight_row = cur.fetchone()

    severity_counter = Counter()
    affected_files = []

    for file_path, severity in files:
        affected_files.append(file_path)
        severity_counter[(severity or "unknown").lower()] += 1

    summary = {"overall_severity": overall_severity}
    for sev, count in severity_counter.items():
        summary[f"{sev}_steps"] = count

    summary["affected_files"] = sorted(set(affected_files))

    return {
    "repo_id": repo_id,
    "run_id": run_id,
    "summary": summary,
    "ai_insight": insight_row[0] if insight_row else None,
    "timestamp": created_at,
    }



# -----------------------------------------------------------------------------
# Read operations
# -----------------------------------------------------------------------------
def fetch_latest_simulation_report(repo_id: str):
    conn = _get_conn()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT run_id, overall_severity, created_at
            FROM simulation_runs
            WHERE repo_id = %s
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (repo_id,),
        )
        row = cur.fetchone()

    if not row:
        return None

    return _build_report_payload(repo_id, row)




def fetch_simulation_report(repo_id: str, run_id: str):
    conn = _get_conn()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT run_id, overall_severity, created_at
            FROM simulation_runs
            WHERE repo_id = %s AND run_id = %s
            LIMIT 1
            """,
            (repo_id, run_id),
        )
        row = cur.fetchone()

    if not row:
        return None

    return _build_report_payload(repo_id, row)



def fetch_severity_summary() -> Dict[str, int]:
    conn = _get_conn()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT LOWER(COALESCE(overall_severity, 'unknown')), COUNT(*)
            FROM simulation_runs
            GROUP BY 1
            """
        )
        rows = cur.fetchall()

    summary = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for sev, count in rows:
        if sev in summary:
            summary[sev] = count

    return summary

def store_performance_run(repo_id: str, run_id: str, data: Dict[str, Any]) -> bool:
    try:
        conn = _get_conn()

        metrics = data.get("metrics", {})
        req = metrics.get("requests", {})
        rt = metrics.get("response_time", {})
        vus = metrics.get("virtual_users", {})

        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO performance_runs (
                    repo_id,
                    run_id,
                    target_url,
                    test_type,
                    duration,
                    vus_max,
                    vus_avg,
                    total_requests,
                    successful_requests,
                    failed_requests,
                    success_rate,
                    failure_rate,
                    avg_response_time,
                    min_response_time,
                    max_response_time,
                    p50_response_time,
                    p95_response_time,
                    p99_response_time
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    repo_id,
                    run_id,
                    data.get("target_url"),
                    data.get("config", {}).get("test_type"),
                    data.get("config", {}).get("duration"),
                    vus.get("max"),
                    vus.get("avg"),
                    req.get("total"),
                    req.get("successful"),
                    req.get("failed"),
                    req.get("success_rate"),
                    req.get("failed_rate"),
                    rt.get("avg"),
                    rt.get("min"),
                    rt.get("max"),
                    rt.get("p50"),
                    rt.get("p95"),
                    rt.get("p99"),
                ),
            )

        return True

    except Exception as e:
        print("Failed storing performance metrics:", e)
        return False



def fetch_performance_run(run_id: str):
    try:
        conn = _get_conn()

        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    repo_id,
                    run_id,
                    target_url,
                    test_type,
                    duration,
                    vus_max,
                    vus_avg,
                    total_requests,
                    successful_requests,
                    failed_requests,
                    success_rate,
                    failure_rate,
                    avg_response_time,
                    min_response_time,
                    max_response_time,
                    p50_response_time,
                    p95_response_time,
                    p99_response_time,
                    created_at
                FROM performance_runs
                WHERE run_id = %s
                LIMIT 1
                """,
                (run_id,)
            )

            row = cur.fetchone()

        if not row:
            return None

        return {
            "repo_id": row[0],
            "run_id": row[1],
            "target_url": row[2],
            "test_type": row[3],
            "duration": row[4],
            "vus_max": row[5],
            "vus_avg": row[6],
            "total_requests": row[7],
            "successful_requests": row[8],
            "failed_requests": row[9],
            "success_rate": row[10],
            "failure_rate": row[11],
            "avg_response_time": row[12],
            "min_response_time": row[13],
            "max_response_time": row[14],
            "p50_response_time": row[15],
            "p95_response_time": row[16],
            "p99_response_time": row[17],
            "created_at": row[18],
        }

    except Exception as e:
        print("Error fetching performance run:", e)
        return None
    

def _parse_timestamp_from_run_id(run_id: str) -> Optional[str]:
    """
    Extract the ISO timestamp embedded in run_ids like
    'NodeGoat_20260117T142921436766'  →  '2026-01-17T14:29:21'
    Returns None if the run_id doesn't match the expected pattern.
    """
    import re
    match = re.search(r"_(\d{8}T\d{6})", run_id)
    if not match:
        return None
    raw = match.group(1)  # e.g. "20260117T142921"
    try:
        from datetime import datetime
        dt = datetime.strptime(raw, "%Y%m%dT%H%M%S")
        return dt.isoformat()
    except ValueError:
        return None


def fetch_dashboard_metrics() -> Dict[str, Any]:
    """
    Return all KPIs needed by the Security Dashboard.

    Sources data from affected_files + ai_insights because simulation_runs
    may not always be populated (data flows through affected_files first).

    Returned shape:
    {
        "repos_analyzed":             int,
        "total_scans":                int,
        "total_vulnerabilities":      int,
        "vulnerability_distribution": {"critical": int, "high": int, "medium": int, "low": int},
        "avg_risk_score":             float,   # 0–10
        "gemini_scans":               int,
        "fallback_scans":             int,
        "last_scan":                  str | None,  # ISO-8601
    }
    """
    conn = _get_conn()
    severity_weights = {"critical": 9.5, "high": 8.5, "medium": 6.0, "low": 3.0}

    with conn.cursor() as cur:
        # ── repos & scans ────────────────────────────────────────────────────
        cur.execute(
            """
            SELECT
                COUNT(DISTINCT repo_id)  AS repos_analyzed,
                COUNT(DISTINCT run_id)   AS total_scans,
                COUNT(*)                 AS total_vulnerabilities
            FROM affected_files
            """
        )
        row = cur.fetchone()
        repos_analyzed: int      = int(row[0] or 0)
        total_scans: int         = int(row[1] or 0)
        total_vulnerabilities: int = int(row[2] or 0)

        # ── vulnerability distribution ────────────────────────────────────────
        cur.execute(
            """
            SELECT LOWER(COALESCE(severity, 'unknown')), COUNT(*)
            FROM affected_files
            GROUP BY 1
            """
        )
        vuln_dist: Dict[str, int] = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for sev, cnt in cur.fetchall():
            if sev in vuln_dist:
                vuln_dist[sev] = int(cnt)

        # ── avg risk score: dominant severity per run → averaged ──────────────
        # For each run pick the most frequent severity label, map to score.
        cur.execute(
            """
            SELECT
                run_id,
                LOWER(COALESCE(severity, 'unknown')) AS sev,
                COUNT(*)                              AS cnt
            FROM affected_files
            GROUP BY run_id, sev
            """
        )
        run_sev_counts: Dict[str, Dict[str, int]] = {}
        for run_id, sev, cnt in cur.fetchall():
            run_sev_counts.setdefault(run_id, {})[sev] = int(cnt)

        run_scores = []
        for sev_counts in run_sev_counts.values():
            dominant = max(sev_counts, key=lambda s: sev_counts[s])
            run_scores.append(severity_weights.get(dominant, 5.0))
        avg_risk_score = round(sum(run_scores) / len(run_scores), 1) if run_scores else 0.0

        # ── gemini vs fallback ────────────────────────────────────────────────
        # A run is "Gemini" when it has an ai_insights row whose insight text
        # is not the fallback sentinel "Gemini unavailable".
        cur.execute(
            """
            SELECT COUNT(DISTINCT run_id)
            FROM ai_insights
            WHERE LOWER(COALESCE(insight, '')) NOT IN ('gemini unavailable', '')
            """
        )
        gemini_scans: int  = int(cur.fetchone()[0] or 0)
        fallback_scans: int = max(0, total_scans - gemini_scans)

        # ── last scan timestamp parsed from run_id ────────────────────────────
        cur.execute(
            """
            SELECT run_id
            FROM affected_files
            ORDER BY run_id DESC
            LIMIT 1
            """
        )
        last_row = cur.fetchone()
        last_scan: Optional[str] = (
            _parse_timestamp_from_run_id(last_row[0]) if last_row else None
        )

        # Fall back to simulation_runs.created_at if run_id parse failed
        if not last_scan:
            try:
                cur.execute("SELECT MAX(created_at) FROM simulation_runs")
                ts_row = cur.fetchone()
                if ts_row and ts_row[0]:
                    last_scan = ts_row[0].isoformat()
            except Exception:
                pass

    return {
        "repos_analyzed":             repos_analyzed,
        "total_scans":                total_scans,
        "total_vulnerabilities":      total_vulnerabilities,
        "vulnerability_distribution": vuln_dist,
        "avg_risk_score":             avg_risk_score,
        "gemini_scans":               gemini_scans,
        "fallback_scans":             fallback_scans,
        "last_scan":                  last_scan,
    }


def fetch_recent_simulations(limit: int = 5) -> list:
    """
    Return the *limit* most recent simulation runs sourced from affected_files
    + ai_insights (simulation_runs is optional enrichment only).

    Each item shape:
    {
        "run_id":            str,
        "repo_id":           str,
        "overall_severity":  str,
        "timestamp":         str | None,
        "total_steps":       int,
        "plan_source":       "gemini" | "fallback",
        "ai_insight":        str | None,
    }
    """
    conn = _get_conn()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                af.run_id,
                af.repo_id,
                COUNT(*)                                        AS attack_vectors,
                MODE() WITHIN GROUP (ORDER BY LOWER(COALESCE(af.severity, 'unknown')))
                                                                AS dominant_severity,
                MIN(
                    CASE
                        WHEN LOWER(COALESCE(ai.insight, '')) NOT IN ('gemini unavailable', '')
                        THEN ai.insight
                    END
                )                                               AS insight,
                SUBSTRING(af.run_id FROM '_([0-9]{8}T[0-9]{6})')  AS run_ts
            FROM affected_files af
            LEFT JOIN ai_insights ai
                   ON ai.run_id  = af.run_id
                  AND ai.repo_id = af.repo_id
            GROUP BY af.run_id, af.repo_id
            ORDER BY run_ts DESC NULLS LAST, af.run_id DESC
            LIMIT %s
            """,
            (limit,),
        )
        rows = cur.fetchall()

    result = []
    for run_id, repo_id, attack_vectors, dominant_severity, insight, _run_ts in rows:
        result.append(
            {
                "run_id":           run_id,
                "repo_id":          repo_id,
                "overall_severity": (dominant_severity or "unknown").lower(),
                "timestamp":        _parse_timestamp_from_run_id(run_id),
                "total_steps":      int(attack_vectors or 0),
                "plan_source":      "gemini" if insight else "fallback",
                "ai_insight":       insight,
            }
        )
    return result


__all__ = [
    "init_snowflake",
    "store_simulation_run",
    "store_affected_files",
    "store_ai_insight",
    "fetch_latest_simulation_report",
    "fetch_simulation_report",
    "fetch_severity_summary",
    "store_performance_run",
    "fetch_performance_run",
    # Dashboard
    "fetch_dashboard_metrics",
    "fetch_recent_simulations",
]