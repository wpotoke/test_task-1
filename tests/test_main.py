import json
import pytest
from unittest.mock import mock_open, patch

from main import CsvReportReader, PayoutReportGenerator, JsonReportRender, ReportCore


# -----------------------
# Fixtures
# -----------------------

@pytest.fixture
def csv_input_salary():
    return """id,email,name,department,hours_worked,salary
1,alice@example.com,Alice Johnson,Marketing,160,50
2,bob@example.com,Bob Smith,Design,150,40
3,dan@example.com,Dan Moroz,Programming,100000,5
"""


@pytest.fixture
def csv_input_hourly_rate():
    return """id,name,department,hours_worked,hourly_rate,email
1,Alice Johnson,Marketing,160,55,alice@example.com
2,Bob Smith,Design,120,35,bob@example.com
3,dan@example.com,Dan Moroz,Programming,100000,5
"""


@pytest.fixture
def employee_data_mixed():
    return {
        "employee_1": {
            "name": "Alice Johnson",
            "department": "Marketing",
            "hours_worked": "160",
            "hourly_rate": "55"
        },
        "employee_2": {
            "name": "Bob Smith",
            "department": "Design",
            "hours_worked": "120",
            "rate": "35"
        },
        "employee_3": {
            "name": "Dan Moroz",
            "department": "Programming",
            "hours_worked": "100000",
            "rate": "5"
        }
    }


# -----------------------
# Reader Tests
# -----------------------

def test_csv_reader_with_salary(csv_input_salary):
    reader = CsvReportReader(["mock.csv"])
    with patch("builtins.open", mock_open(read_data=csv_input_salary)):
        employees = reader.read()
    assert len(employees) == 3
    assert employees["employee_1"]["department"] == "Marketing"
    assert employees["employee_3"]["department"] == "Programming"

def test_csv_reader_with_hourly_rate(csv_input_hourly_rate):
    reader = CsvReportReader(["mock.csv"])
    with patch("builtins.open", mock_open(read_data=csv_input_hourly_rate)):
        employees = reader.read()
    assert employees["employee_2"]["hourly_rate"] == "35"
    assert employees["employee_3"]["hourly_rate"] == "100000"


def test_csv_reader_multiple_files(csv_input_salary, csv_input_hourly_rate):
    reader = CsvReportReader(["file1.csv", "file2.csv"])
    open_mock = mock_open()
    open_mock.side_effect = [
        mock_open(read_data=csv_input_salary).return_value,
        mock_open(read_data=csv_input_hourly_rate).return_value
    ]
    with patch("builtins.open", open_mock):
        employees = reader.read()
    assert len(employees) == 6


# -----------------------
# Generator Tests
# -----------------------

def test_payout_calculation(employee_data_mixed):
    gen = PayoutReportGenerator()
    report = gen.generate(employee_data_mixed)
    assert any(e["payout"] == "$8800" for e in report["Marketing"])
    assert any(e["payout"] == "$4200" for e in report["Design"])
    assert any(e["payout"] == "$500000" for e in report["Programming"])


def test_zero_hours():
    data = {
        "employee_1": {
            "name": "Zero",
            "department": "Test",
            "hours_worked": "0",
            "rate": "100"
        },
        "employee_2": {
            "name": "Danchik",
            "department": "Pytest",
            "hours_worked": "10000000202020020201",
            "rate": "0"
        }
    }
    gen = PayoutReportGenerator()
    result = gen.generate(data)
    assert result["Pytest"][0]["payout"] == "$0"
    assert result["Test"][0]["payout"] == "$0"


def test_empty_department():
    data = {
        "employee_1": {
            "name": "NoDept",
            "department": "",
            "hours_worked": "100",
            "rate": "10"
        }
    }
    gen = PayoutReportGenerator()
    result = gen.generate(data)
    assert "" in result
    assert result[""][0]["payout"] == "$1000"


def test_missing_rate_field():
    data = {
        "employee_1": {
            "name": "MissingRate",
            "department": "Marketing",
            "hours_worked": "100"
        }
    }
    gen = PayoutReportGenerator()
    result = gen.generate(data)
    assert result["Marketing"][0]["payout"] == "$0"


# -----------------------
# Render Tests
# -----------------------

def test_json_render_output():
    renderer = JsonReportRender()
    data = {
        "Design": [
            {"name": "Bob", "hours": "100", "rate": "35", "payout": "$3500"},
            {"total_hours": "100"},
            {"total_payout": "$3500"}
        ]
    }
    output = renderer.render(data)
    parsed = json.loads(output)
    assert parsed["Design"][0]["name"] == "Bob"


# -----------------------
# Core Execution Test
# -----------------------

def test_core_pipeline(monkeypatch):
    data = {
        "employee_1": {
            "name": "Mock",
            "department": "Test",
            "hours_worked": "10",
            "salary": "15"
        }
    }
    reader = CsvReportReader(["fake.csv"])
    generator = PayoutReportGenerator()
    renderer = JsonReportRender()
    app = ReportCore(reader, generator, renderer)

    # Подменяем чтение
    monkeypatch.setattr(reader, "read", lambda: data)

    # Подменяем print
    captured = []
    monkeypatch.setattr("builtins.print", lambda x: captured.append(x))

    # Запускаем
    app.run()

    # --- Проверки:
    assert len(captured) == 1  # только один print

    # Проверка, что это валидный JSON
    try:
        output = json.loads(captured[0])
    except json.JSONDecodeError:
        pytest.fail("Вывод ReportCore не является валидным JSON")

    # Проверка структуры
    assert "Test" in output
    report = output["Test"]
    assert report[0]["name"] == "Mock"
    assert report[0]["hours"] == "10"
    assert report[0]["rate"] == "15"
    assert report[0]["payout"] == "$150"

    # Итоги
    assert {"total_hours": "10"} in report
    assert {"total_payout": "$150"} in report
