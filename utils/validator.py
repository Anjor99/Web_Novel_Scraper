def validate_range(start, end, total=None):
    if end < start:
        raise ValueError("End chapter must be >= start")
    if total and end > total:
        raise ValueError("End exceeds total chapters")
