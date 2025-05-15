---

# Report Generator

Report Generator — это Python-приложение для чтения CSV-файлов с данными сотрудников, генерации отчётов (например, по выплатам) и вывода их в различных форматах (JSON, консоль).

---

### Описание
Недавно мне дали тестовое, первый раз плотно поработал с SOLID и argpars, в проекте есть прототип, и у него есть тоже свои тесты, но не все проходят он просто для наглядности как я начинал писать

---

## 📦 Возможности

* ✅ Чтение данных из одного или нескольких CSV-файлов.
* 📈 Генерация отчёта по выплатам.
* 🖨️ Вывод в JSON или текстовом виде в консоль.
* 🧱 Расширяемая архитектура (через `ABC` — абстрактные базовые классы).
* 🛠️ Обработка ошибок с кастомным `argparse`.

---

## Требования

* Python 3.10+
* Стандартная библиотека Python (`abc`, `argparse`, `json` и т.д.)
  
❗ Не используются сторонние библиотеки.

---

## Пример CSV-файла

```csv
name,hours_worked,rate,department
Alice,40,25,IT
Bob,30,20,HR
Charlie,50,30,IT
```

---

## 🚀 Как запустить

main.py

```bash
python main.py example.csv --report payout --format json
python main.py example.csv --report payout --format console
```

тесты

```bash
pytest tests/test_main.py
pytest tests/test_main.py --cov=main --cov-report=term-missing
```
![image](https://github.com/user-attachments/assets/377f462a-8dd0-4ded-9939-b00502a55635)
![image](https://github.com/user-attachments/assets/bdcb87ca-39bf-4261-991d-44e02adfc7d7)


### Параметры

| Аргумент   | Описание                                        | Обязательный |
| ---------- | ----------------------------------------------- | ------------ |
| `files`    | Один или несколько CSV-файлов                   | ✅            |
| `--report` | Название отчета (`payout`)                      | ✅            |
| `--format` | Формат вывода: `json` (по умолчанию), `console` | ❌            |

---

## Пример вывода

### В формате JSON:

```json
{
    "IT": [
        {
            "name": "Alice",
            "hours": "40",
            "rate": "25",
            "payout": "$1000"
        },
        ...
        {
            "total_hours": "90"
        },
        {
            "total_payout": "$2500"
        }
    ],
    "HR": [
        ...
    ]
}
```

### В консоль:

```
IT
-------------------------

name      hours      rate      payout
Alice     40         25        $1000
...

total_hours
90

total_payout
$2500
```

---

## Расширение функциональности

Ты можешь легко добавить:

* ✅ **Новый тип отчета** — создай класс, унаследованный от `ReportGenerator`
* ✅ **Новый формат вывода** — создай класс, унаследованный от `ReportRender`
* ✅ **Новый источник данных** — создай класс, унаследованный от `ReportReader`

Просто зарегистрируй их в словарях `aviable_reports`, `aviable_renders`, `aviable_readers`.

---

## Обработка ошибок

- Некорректный файл → Файл не найден
- Отсутствующий аргумент → Error paremeters
- Отсутствующее поле → сообщение об ошибке и $0 в payout

---
