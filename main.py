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
    parser.add_argument("--report", type=str, help="Путь к файлу для сохранения отчета")
    parser.add_argument("--report-type", choices=REPORT_TYPES.keys(), default="handler", help="Тип отчета")
    return parser.parse_args()


def main() -> None:
    """
    Парсит аргументы командной строки, обрабатывает указанные лог-файлы, объединяет полученную статистику,
    генерирует отчет, выводит его в консоль и сохраняет в файл, если указан аргумент --report.
    """
    args = parse_args()
    report_class: type[BaseReport] = REPORT_TYPES[args.report_type]

    aggregate = report_class.get_initial_aggregate()

    with ProcessPoolExecutor() as executor:
        futures = {
            executor.submit(report_class.process_file, path): path
            for path in args.log_files
        }
        for future in as_completed(futures):
            result = future.result()
            report_class.merge(aggregate, result)

    report_str = report_class.generate(aggregate)
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
