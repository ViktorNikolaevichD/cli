from abc import ABC, abstractmethod
from typing import Any


class BaseReport(ABC):
    @classmethod
    @abstractmethod
    def process_file(cls, log_file_path: str) -> Any:
        ...

    @classmethod
    @abstractmethod
    def get_initial_aggregate(cls) -> Any:
        ...

    @classmethod
    @abstractmethod
    def merge(cls, base: Any, new: Any) -> Any:
        ...

    @classmethod
    @abstractmethod
    def generate_report(cls, data: Any) -> str:
        ...

    @classmethod
    @abstractmethod
    def count_total_requests(cls, data: Any) -> int:
        ...
