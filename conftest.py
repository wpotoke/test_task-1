import pytest


@pytest.fixture
def csv_input_salary():
    return """id,email,name,department,hours_worked,salary
1,alice@example.com,Alice Johnson,Marketing,160,50
2,bob@example.com,Bob Smith,Design,150,40
"""


@pytest.fixture
def csv_input_hourly_rate():
    return """id,name,department,hours_worked,hourly_rate,email
1,Alice Johnson,Marketing,160,55,alice@example.com
2,Bob Smith,Design,120,35,bob@example.com
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
        }
    }
