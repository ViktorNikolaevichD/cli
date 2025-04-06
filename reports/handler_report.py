from reports.base import BaseReport
from utils.common import HANDLER_HEADER, STANDARD_LEVELS, get_empty_counts


class HandlerReport(BaseReport):
    @classmethod
    def process_file(cls, log_file_path: str) -> dict[str, dict[str, int]]:
        """
        Обрабатывает лог-файл и возвращает статистику по количеству записей для каждого handler
        по уровням логирования.
        """
        handler_counts: dict[str, dict[str, int]] = {}

        try:
            with open(log_file_path, "r", encoding="utf-8") as file:
                for line in file:
                    if "django.request:" not in line:
                        continue

                    parts = line.split()
                    if len(parts) < 3:
                        continue

                    level = parts[2]

                    index = line.find("django.request:")
                    if index == -1:
                        continue
                    
                    after = line[index + len("django.request:"):]
                    tokens = after.split()
                    url = None
                    for token in tokens:
                        if token.startswith("/"):
                            url = token
                            break
                    if url is None:
                        continue

                    if url not in handler_counts:
                        handler_counts[url] = get_empty_counts()
                    
                    if level in STANDARD_LEVELS:
                        handler_counts[url][level] += 1
        except FileNotFoundError:
            print(f"Файл {log_file_path} не найден")
        except Exception as e:
            print(f"Ошибка при чтении файла {log_file_path}: {e}")
        
        return handler_counts

    @classmethod
    def get_initial_aggregate(cls) -> dict[str, dict[str, int]]:
        return {}
    
    @classmethod
    def merge(cls, base: dict[str, dict[str, int]], new: dict[str, dict[str, int]]) -> None:
        """
        Объединяет статистику из отчетов.
        """
        for handler, levels in new.items():
            if handler not in base:
                base[handler] = get_empty_counts()
            for level, count in levels.items():
                base[handler][level] += count
    
    @classmethod
    def generate_report(cls, data: dict[str, dict[str, int]]) -> str:
        """
        Собирает строки отчета в виде таблицы по переданным данным.
        """
        lines = [
            f"Total requests: {cls.count_total_requests(data)}",
            HANDLER_HEADER,
        ]
        total = get_empty_counts()

        for handler in sorted(data.keys()):
            row = data[handler]
            lines.append(
                f"{handler:30}{row['DEBUG']:8}{row['INFO']:8}{row['WARNING']:8}{row['ERROR']:8}{row['CRITICAL']:10}"
            )
            for level in total:
                total[level] += row.get(level, 0)
        
        lines.append(
            f"{'TOTAL':30}{total['DEBUG']:8}{total['INFO']:8}{total['WARNING']:8}{total['ERROR']:8}{total['CRITICAL']:10}"
        )
        return "\n".join(lines)

    @classmethod
    def count_total_requests(cls, data: dict[str, dict[str, int]]) -> int:
        """
        Выполняет подсчет количества запросов.
        """
        total = 0
        for levels in data.values():
            total += sum(levels.values())
        return total
