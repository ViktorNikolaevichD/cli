import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed

from reports import REPORT_TYPES
from reports.base import BaseReport


def parse_args() -> argparse.Namespace:
    """
    Парсит аргументы командной строки.
    """
    parser = argparse.ArgumentParser(description="Отчет по лог-файлам")
    parser.add_argument("log_files", nargs="+", help="Пути к лог-файлам")
    parser.add_argument("--report", choices=REPORT_TYPES.keys(), help="Тип отчета")
    return parser.parse_args()


def main() -> None:
    """
    Парсит аргументы командной строки, обрабатывает указанные лог-файлы, объединяет полученную статистику
    и выводит отчет в консоль.
    """
    args = parse_args()
    report_class: type[BaseReport] = REPORT_TYPES[args.report]

    aggregate = report_class.get_initial_aggregate()

    with ProcessPoolExecutor() as executor:
        futures = {
            executor.submit(report_class.process_file, path): path
            for path in args.log_files
        }
        for future in as_completed(futures):
            result = future.result()
            report_class.merge(aggregate, result)

    report_str = report_class.generate_report(aggregate)
    print(report_str)


if __name__ == "__main__":
    main()
