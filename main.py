import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed

STANDARD_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
HEADER = f"{'HANDLER':30}{'DEBUG':>8}{'INFO':>8}{'WARNING':>8}{'ERROR':>8}{'CRITICAL':>10}"


def get_empty_counts() -> dict[str, int]:
    """
    Возвращает новый словарь-счётчик для уровней логирования.
    """
    return {"DEBUG": 0, "INFO": 0, "WARNING": 0, "ERROR": 0, "CRITICAL": 0}


def process_file(log_file_path: str) -> dict[str, dict[str, int]]:
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


def merge_counts(
    base: dict[str, dict[str, int]],
    new_counts: dict[str, dict[str, int]],
) -> None:
    """
    Объединяет статистику из new_counts в общий словарь base.
    Для каждого handler из new_counts суммирует значения по уровням логирования в словаре base.
    """
    for handler, levels in new_counts.items():
        if handler not in base:
            base[handler] = get_empty_counts()
        for level, count in levels.items():
            base[handler][level] += count


def print_report(counts: dict[str, dict[str, int]]) -> None:
    """
    Выводит отчет в консоль в виде таблицы с подсчетом записей по уровням логирования для каждого handler.
    Также выводится итоговая строка с суммарными значениями.
    """
    print(HEADER)

    for handler in sorted(counts.keys()):
        row = counts[handler]
        print(f"{handler:30}{row['DEBUG']:8}{row['INFO']:8}{row['WARNING']:8}{row['ERROR']:8}{row['CRITICAL']:10}")

    total = get_empty_counts()
    for levels in counts.values():
        for level in total:
            total[level] += levels.get(level, 0)
    print(f"{'TOTAL':30}{total['DEBUG']:8}{total['INFO']:8}{total['WARNING']:8}{total['ERROR']:8}{total['CRITICAL']:10}")


def build_report_lines(counts: dict[str, dict[str, int]]) -> list[str]:
    """
    Собирает строки отчета в виде таблицы по переданным данным.
    """
    lines = []
    lines.append(HEADER)

    for handler in sorted(counts.keys()):
        row = counts[handler]
        lines.append(
            f"{handler:30}{row['DEBUG']:8}{row['INFO']:8}{row['WARNING']:8}{row['ERROR']:8}{row['CRITICAL']:10}"
        )

    total = get_empty_counts()
    for levels in counts.values():
        for level in total:
            total[level] += levels.get(level, 0)
    lines.append(
        f"{'TOTAL':30}{total['DEBUG']:8}{total['INFO']:8}{total['WARNING']:8}{total['ERROR']:8}{total['CRITICAL']:10}"
    )
    return lines


def generate_report(overall_counts: dict[str, dict[str, int]]) -> str:
    """
    Генерирует текстовый отчет в виде таблицы с подсчетом записей по уровням логирования
    для каждого handler, а также добавляет итоговую строку со сводными значениями.
    """
    return "\n".join(build_report_lines(overall_counts))
  

def parse_args() -> argparse.Namespace:
    """
    Парсит аргументы командной строки.
    """
    parser = argparse.ArgumentParser(description="Отчет по лог-файлам")
    parser.add_argument("log_files", nargs="+", help="Пути к лог-файлам")
    parser.add_argument("--report", type=str, help="Путь к файлу для сохранения отчета")
    return parser.parse_args()


def main() -> None:
    """
    Парсит аргументы командной строки, обрабатывает указанные лог-файлы, объединяет полученную статистику,
    генерирует отчет, выводит его в консоль и сохраняет в файл, если указан аргумент --report.
    """
    args = parse_args()
    log_files: list[str] = args.log_files

    overall_counts: dict[str, dict[str, int]] = {}

    with ProcessPoolExecutor() as executor:
        future_to_file = {executor.submit(process_file, file_path): file_path for file_path in log_files}
        for future in as_completed(future_to_file):
            file_counts = future.result()
            merge_counts(overall_counts, file_counts)

    report_str = generate_report(overall_counts)
    print(report_str)

    if args.report:
        try:
            with open(args.report, "w", encoding="utf-8") as out_file:
                out_file.write(report_str)
            print(f"\nОтчет сохранен в файл: {args.report}")
        except Exception as e:
            print(f"Ошибка при записи отчета в файл {args.report}: {e}")


if __name__ == "__main__":
    main()
