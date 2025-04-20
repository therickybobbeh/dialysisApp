from datetime import datetime, time, timezone
from typing import Optional, Tuple

def normalize_to_utc_day_bounds(
    start: Optional[datetime],
    end:   Optional[datetime]
) -> Tuple[Optional[datetime], Optional[datetime]]:
    """
    Given optional datetimes, returns a tuple of:
      - start at 00:00:00 UTC of that day (or None)
      - end   at 23:59:59.999999 UTC of that day (or None)
    """
    start_dt = None
    end_dt = None

    if start is not None:
        # set to start of day in UTC
        start_dt = datetime.combine(start.date(), time.min, tzinfo=timezone.utc)
    if end is not None:
        # set to end of day in UTC
        end_dt = datetime.combine(end.date(), time.max, tzinfo=timezone.utc)

    return start_dt, end_dt
