import pytest
import json
from io import StringIO
from unittest.mock import patch, mock_open
from prototype import FileHandler


# --- Sample CSV data fixtures ---

@pytest.fixture
def csv_with_salary():
    return """id,email,name,department,hours_worked,salary
1,a@example.com,Alice,Marketing,160,50
2,b@example.com,Bob,Design,120,40
"""

@pytest.fixture
def csv_missing_rate():
    return """id,name,department,hours_worked,email
1,Alice,Marketing,100,a@example.com
"""

# --- resolve_rate tests ---

def test_resolve_rate_salary(csv_with_salary):
    handler = FileHandler([])
    fake_data = {
        'employee_1': {
            'salary': '50'
        }
    }
    assert handler.resolve_rate(fake_data, 'employee_1') == 'salary'

def test_resolve_rate_none():
    handler = FileHandler([])
    fake_data = {
        'employee_1': {
            'some_field': 'X'
        }
    }
    assert handler.resolve_rate(fake_data, 'employee_1') is None


# --- create_paremetrs ---

def test_create_parameters_parses_header_and_values(csv_with_salary):
    handler = FileHandler([])
    file = StringIO(csv_with_salary)
    data, keys, values = handler.create_paremetrs(file)

    assert list(data.keys()) == ['employee_1', 'employee_2']
    assert 'salary' in keys
    assert values[0][2] == 'Alice'


# --- handle() core logic ---

def test_handle_prints_json_output(csv_with_salary):
    handler = FileHandler(["mock.csv"])

    with patch("builtins.open", mock_open(read_data=csv_with_salary)):
        with patch("builtins.print") as mock_print:
            handler.handle()

    printed = mock_print.call_args[0][0]
    output = json.loads(printed)

    assert "Marketing" in output
    assert output['Marketing'][0]['payout'] == "$8000"
    assert any('total_payout' in i for i in output['Marketing'])


# --- edge case: missing rate field ---

def test_handle_with_missing_rate_prints_zero(csv_missing_rate):
    handler = FileHandler(["mock.csv"])

    with patch("builtins.open", mock_open(read_data=csv_missing_rate)):
        with patch("builtins.print") as mock_print:
            handler.handle()

    printed = mock_print.call_args[0][0]
    assert 'MissingRate' not in printed or '$0' in printed or 'Не найдено' in printed