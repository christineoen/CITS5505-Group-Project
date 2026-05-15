DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def fmt_date(d):
    """Format a date as 'Mon, 5 Aug 2026' without platform-specific strftime flags."""
    return d.strftime('%a, %d %b %Y').replace(' 0', ' ')


def fmt_time(t):
    """Format a time/datetime as '3:00 PM' without platform-specific strftime flags."""
    return t.strftime('%I:%M %p').lstrip('0')
