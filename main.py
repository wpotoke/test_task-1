from abc import ABC, abstractmethod
import argparse
import json


class ReportGenerator(ABC):
    """Абстрактный класс для генерации отчета
    Создан чтобы иметь возоможность генерировать различные отчеты"""

    @abstractmethod
    def generate(self, employees: dict[dict:str]) -> dict[str]: ...


class ReportReader(ABC):
    """Абстрактный класс для чтения отчета
    Создан чтобы иметь возоможность читать отчеты в разных форматах"""

    @abstractmethod
    def read(self): ...


class ReportRender(ABC):
    """Абстрактный класс для вывода отчета
    Создан чтобы иметь возоможность выводить отчеты в разных форматах"""

    @abstractmethod
    def render(self, employees): ...


class ReportCore:
    """Ядро приложения, инициализация всех классов и запуск функции run"""

    def __init__(
        self, reader: ReportReader, generator: ReportGenerator, render: ReportRender
    ):
        self.reader = reader
        self.generator = generator
        self.render = render

    def run(self):
        employees = self.reader.read()
        report = self.generator.generate(employees)
        output = self.render.render(report)
        print(output)


class CsvReportReader(ReportReader):
    """Класс для чтения отчета в формате csv"""

    def __init__(self, files):
        self.files = files

    def read(self):
        employees = {}
        emp_id = 1

        for file_name in self.files:
            with open(file_name, "r", encoding="utf-8") as file:
                lines = file.readlines()
                keys = lines[0].strip().split(",")

                for line in lines[1:]:
                    values = line.strip().split(",")
                    employees[f"employee_{emp_id}"] = dict(zip(keys, values))
                    emp_id += 1
        return employees
    


class PayoutReportGenerator(ReportGenerator):
    """Класс для генерации отчета payout"""

    def resolve_rate(self, data, key):
        valid_value = ["rate", "hourly_rate", "salary"]

        for i in valid_value:
            if i in data[key]:
                return i
        return None

    def generate(self, employees):
        dict_output = {}

        for i, k in enumerate(employees):
            rate = self.resolve_rate(employees, k)
            try:
                if rate is None:
                    raise ValueError("Не найдено поле ставки для сотрудника")
                employees[k]["_rate_field"] = rate
                employees[k]["payout"] = "$" + str(
                    int(employees[k]["hours_worked"]) * int(employees[k][rate])
                )
            except (ValueError, KeyError, TypeError) as e:
                print(e)
                employees[k]["_rate_field"] = ""
                employees[k]["payout"] = "$0"

        departments_payout = {employees[i]["department"]: 0 for i in employees}
        department_hours = {employees[i]["department"]: 0 for i in employees}
        department_names = sorted(
            list(set([employees[i]["department"] for i in employees]))
        )

        for i in employees:
            departments_payout[employees[i]["department"]] += int(
                employees[i]["payout"][1:]
            )
            department_hours[employees[i]["department"]] += int(
                employees[i]["hours_worked"]
            )

        for i in employees.values():
            rate_field = i["_rate_field"]
            if i["department"] in department_names:
                if i["department"] not in dict_output:
                    dict_output[i["department"]] = [
                        {
                            "name": i.get("name", "Unknown"),
                            "hours": i.get("hours_worked", "0"),
                            "rate": i.get(rate_field, "0"),
                            "payout": i.get("payout", "0"),
                        }
                    ]
                else:
                    dict_output[i["department"]].append(
                        {
                            "name": i.get("name", "Unknown"),
                            "hours": i.get("hours_worked", "0"),
                            "rate": i.get(rate_field, "0"),
                            "payout": i.get("payout", "0"),
                        }
                    )

        for k, v in department_hours.items():
            dict_output[k].append({"total_hours": str(v)})

        for k, v in departments_payout.items():
            dict_output[k].append({"total_payout": "$" + str(v)})

        return dict_output


class JsonReportRender(ReportRender):
    """Класс для вывода отчета в формате json"""

    def render(self, employees):
        return json.dumps(employees, indent=4, ensure_ascii=False)


class ConsoleReportRender(ReportRender):
    """Класс для вывода отчета в console"""

    def render(self, employees):
        for k, v in employees.items():
            print("\n" + k + "\n" + "-" * 25 + "\n")
            for i in v:
                keys = "      ".join(i.keys())
                values = "   ".join(str(val) for val in i.values())
                print(keys)
                print(values)
                print()


class CustomArgumentParser(argparse.ArgumentParser):
    """Кастомный парсер, переопределен метод error для отлова ошибки"""

    def error(self, message):
        try:
            raise ValueError("Error paremeters")
        except ValueError as e:
            print(e)
            print(message)
            print(self.print_help())
            exit(1)


if __name__ == "__main__":

    parser = CustomArgumentParser(description="Csv to json")

    parser.add_argument("files", nargs="+", help="Список файлов")
    parser.add_argument(
        "--report", type=str, required=True, help="Название отчёта (например: payout)"
    )
    parser.add_argument(
        "--format",
        type=str,
        default="json",
        help="Формат вывода: json (по умолчанию) или console",
    )

    args = parser.parse_args()

    aviable_reports = {
        "payout": PayoutReportGenerator,
        # "avg_rate_in_hour": AvgRateReportGenerator
    }
    aviable_renders = {
        "json": JsonReportRender,
        "console": ConsoleReportRender,
    }
    aviable_readers = {"csv": CsvReportReader}

    if args.report not in aviable_reports:
        print(
            f"Отчёт {args.report} не поддерживается, доступны {', '.join(aviable_reports.keys())}"
        )
        exit(1)

    if args.format not in aviable_renders:
        print(
            f"Формат {args.format} не  поддерживается, доступны {', '.join(aviable_renders.keys())}"
        )
        exit(1)

    files = args.files
    reader = aviable_readers["csv"](files)
    generator = aviable_reports[args.report]()
    renderer = aviable_renders[args.format]()

    app = ReportCore(reader, generator, renderer)
    try:
        app.run()
    except FileNotFoundError as e:
        print("Файл не найден")
    except ValueError as e:
        print("Ошибка значения")
