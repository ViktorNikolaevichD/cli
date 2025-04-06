import os
import sys

from main import (
    generate_report, 
    get_empty_counts, 
    merge_counts, 
    process_file, 
    HEADER, 
    parse_args,
)

TEST_LOG1 = os.path.join(os.path.dirname(__file__), "mock_data/mock_log1.log")
TEST_LOG2 = os.path.join(os.path.dirname(__file__), "mock_data/mock_log2.log")


def test_get_empty_counts():
    """
    Тест: функция возвращает словарь с ключами
    """

    counts = get_empty_counts()
    expected_keys = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    assert set(counts.keys()) == expected_keys
    for key in expected_keys:
        assert counts[key] == 0


def test_process_file_log1():
    """
    Тест: правильно вычисляется количество записей в логах
    """
    result = process_file(TEST_LOG1)
    assert "/api/v1/reviews/" in result
    assert "/admin/dashboard/" in result

    reviews_counts = result["/api/v1/reviews/"]
    assert reviews_counts["INFO"] == 2
    assert reviews_counts["DEBUG"] == 0
    assert reviews_counts["WARNING"] == 0
    assert reviews_counts["ERROR"] == 0
    assert reviews_counts["CRITICAL"] == 0

    admin_counts = result["/admin/dashboard/"]
    assert admin_counts["INFO"] == 1
    assert admin_counts["ERROR"] == 1
    assert admin_counts["DEBUG"] == 0
    assert admin_counts["WARNING"] == 0
    assert admin_counts["CRITICAL"] == 0

    # Проверить правильность выполнения для второго файла
    result = process_file(TEST_LOG2)
    assert "/admin/dashboard/" in result
    assert "/api/v1/checkout/" in result

    admin_counts = result["/admin/dashboard/"]
    assert admin_counts["INFO"] == 1
    assert admin_counts["ERROR"] == 1
    assert admin_counts["DEBUG"] == 0
    assert admin_counts["WARNING"] == 0
    assert admin_counts["CRITICAL"] == 0

    checkout_counts = result["/api/v1/checkout/"]
    assert checkout_counts["ERROR"] == 1
    assert checkout_counts["DEBUG"] == 0
    assert checkout_counts["INFO"] == 0
    assert checkout_counts["WARNING"] == 0
    assert checkout_counts["CRITICAL"] == 0



def test_merge_counts_and_generate_report():
    """
    Тест: объединет статистику из двух файлов и генерирует отчет
    """
    result1 = {
        '/api/v1/reviews/': {
            'DEBUG': 0, 
            'INFO': 2, 
            'WARNING': 0, 
            'ERROR': 0, 
            'CRITICAL': 0
        }, 
        '/admin/dashboard/': {
            'DEBUG': 0, 
            'INFO': 1, 
            'WARNING': 0, 
            'ERROR': 1, 
            'CRITICAL': 0
        }
    }
    result2 = {
        "/admin/dashboard/": {
            "DEBUG": 0, 
            "INFO": 1, 
            "WARNING": 0, 
            "ERROR": 1, 
            "CRITICAL": 0
        }, 
        "/api/v1/checkout/": {
            "DEBUG": 0, 
            "INFO": 0, 
            "WARNING": 0, 
            "ERROR": 1, 
            "CRITICAL": 0
        }
    }

    overall = {}
    merge_counts(overall, result1)
    merge_counts(overall, result2)

    reviews_counts = overall.get("/api/v1/reviews/")
    assert reviews_counts is not None
    assert reviews_counts["INFO"] == 2

    admin_counts = overall.get("/admin/dashboard/")
    assert admin_counts is not None
    assert admin_counts["INFO"] == 2
    assert admin_counts["ERROR"] == 2

    checkout_counts = overall.get("/api/v1/checkout/")
    assert checkout_counts is not None
    assert checkout_counts["ERROR"] == 1


def test_generate_report():
    """
    Тест: создание отчета содержит необходимую информацию
    """
    overall = {
        "/api/v1/reviews/": {
            "DEBUG": 0, 
            "INFO": 2, 
            "WARNING": 0, 
            "ERROR": 0, 
            "CRITICAL": 0
        }, 
        "/admin/dashboard/": {
            "DEBUG": 0, 
            "INFO": 2, 
            "WARNING": 0, 
            "ERROR": 2, 
            "CRITICAL": 0
        }, 
        "/api/v1/checkout/": {
            "DEBUG": 0, 
            "INFO": 0, 
            "WARNING": 0, 
            "ERROR": 1, 
            "CRITICAL": 0
        }
    }
    report = generate_report(overall)
    assert HEADER in report
    assert "TOTAL" in report
    assert "/admin/dashboard/" in report
    assert "/api/v1/checkout/" in report
    assert "/api/v1/reviews/" in report


def test_parse_args(monkeypatch):
    """
    Тест: функция parse_args верно парсит аргументы командной строки.
    """
    test_args = ["main.py", "file1.log", "file2.log", "--report", "report.txt"]
    monkeypatch.setattr(sys, "argv", test_args)
    args = parse_args()
    assert args.log_files == ["file1.log", "file2.log"]
    assert args.report == "report.txt"

    test_args = ["main.py", "file1.log", "file2.log"]
    monkeypatch.setattr(sys, "argv", test_args)
    args = parse_args()
    assert args.log_files == ["file1.log", "file2.log"]
    assert args.report == None
