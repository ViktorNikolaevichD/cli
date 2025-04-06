STANDARD_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
HANDLER_HEADER = f"{'HANDLER':30}{'DEBUG':>8}{'INFO':>8}{'WARNING':>8}{'ERROR':>8}{'CRITICAL':>10}"


def get_empty_counts() -> dict[str, int]:
    """
    Возвращает новый словарь-счётчик для уровней логирования.
    """
    return {"DEBUG": 0, "INFO": 0, "WARNING": 0, "ERROR": 0, "CRITICAL": 0}
