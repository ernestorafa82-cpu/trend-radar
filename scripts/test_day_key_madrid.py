from datetime import datetime, timezone
from zoneinfo import ZoneInfo

def day_key(dt):
    return dt.astimezone(ZoneInfo("Europe/Madrid")).strftime("%Y-%m-%d")

dt = datetime(2026, 2, 14, 23, 30, tzinfo=timezone.utc)
print("utc:", dt.isoformat())
print("madrid_day_key:", day_key(dt))
