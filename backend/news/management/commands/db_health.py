import time
from django.db import connection

def database_is_slow(threshold_ms=150):
    """
    Quick DB health check.
    If SELECT 1 takes longer than `threshold_ms`, DB is considered slow.
    """
    start = time.monotonic()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
    except Exception:
        return True  # DB unreachable
    duration_ms = (time.monotonic() - start) * 1000
    return duration_ms > threshold_ms
