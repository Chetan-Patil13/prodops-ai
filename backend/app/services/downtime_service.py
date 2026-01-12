from sqlalchemy import text
from app.db.connection import engine


def get_downtime_summary(line_code: str, date: str):
    """
    Returns downtime summary grouped by reason.
    """
    sql = text("""
        SELECT
            d.reason_code,
            d.reason_text,
            SUM(EXTRACT(EPOCH FROM (d.end_time - d.start_time)) / 60) AS downtime_minutes
        FROM downtime_log d
        JOIN production_lines pl ON d.line_id = pl.id
        WHERE pl.line_code = :line_code
          AND DATE(d.start_time) = :dt_date
        GROUP BY d.reason_code, d.reason_text
        ORDER BY downtime_minutes DESC;
    """)

    with engine.connect() as conn:
        rows = conn.execute(
            sql,
            {"line_code": line_code, "dt_date": date}
        ).mappings().all()

    return rows
