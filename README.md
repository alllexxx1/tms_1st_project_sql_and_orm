# Сервис резервирования билетов

Учебная практика на 3 часа по работе с PostgreSQL из Python.
Сначала реализуем операции на raw SQL через Psycopg, затем повторим их
на SQLAlchemy с миграциями Alembic. В обеих версиях пользователь выбирает
мероприятие, ряд и номер места.

Практика рассчитана на студентов, знакомых с функциями, классами,
аннотациями типов, `with`, базовыми SQL-запросами, ключами и JOIN.

## Текущий этап

Версия на raw SQL готова: CRUD мероприятий и мест, поиск, свободные места,
бронирование и отмена билетов. Все операции вызываем как отдельные функции
из консоли Python. Следующий этап – модели SQLAlchemy и миграции Alembic.
План занятия и этапы реализации описаны в [docs/practice_plan.md](docs/practice_plan.md).

## Подготовка

Нужны установленный Python 3.15, работающий PostgreSQL и клиент для SQL-запросов
(например, DBeaver или pgAdmin). Команды выполняются из корня проекта.

### 1. Виртуальное окружение и зависимости

Если `.venv` уже существует, повторно создавать его не нужно.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

В Windows PowerShell создание и активация окружения выглядят так:

```powershell
py -3.15 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Версии прямых зависимостей зафиксированы для повторения практики:

| Библиотека | Версия | Назначение |
| --- | --- | --- |
| Psycopg с готовым бинарным драйвером | 3.3.6 | Подключение к PostgreSQL и raw SQL |
| SQLAlchemy | 2.1.5 | ORM |
| Alembic | 1.20.0 | Миграции схемы БД |
| python-dotenv | 1.2.4 | Загрузка настроек из `.env` |

Версии сверены 19 октября 2026 года. SQLAlchemy 2.1.5 является текущим
стабильным релизом. Для ORM будем использовать `DeclarativeBase`, `Mapped`,
`mapped_column`, `select()` и `Session`.

Источники: [релизы SQLAlchemy](https://www.sqlalchemy.org/download.html),
[ORM Quick Start](https://docs.sqlalchemy.org/en/21/orm/quickstart.html),
[релизы Psycopg](https://www.psycopg.org/psycopg3/docs/news.html),
[релизы Alembic](https://alembic.sqlalchemy.org/en/latest/changelog.html),
[python-dotenv](https://pypi.org/project/python-dotenv/).

### 2. Учебные базы данных

Подключитесь к PostgreSQL через привычный клиент под пользователем,
которому разрешено создавать роли и базы. Выполните команды отдельно,
вне блока транзакции; в клиенте должен быть включен autocommit:

```sql
CREATE ROLE ticket_student WITH LOGIN PASSWORD 'password';
CREATE DATABASE ticket_booking_raw OWNER ticket_student;
CREATE DATABASE ticket_booking_orm OWNER ticket_student;
```

Это две независимые базы с одинаковой предметной областью. Первую создадим
SQL-скриптом, вторую будем развивать миграциями Alembic. Так обе версии смогут
работать независимо, а Alembic получит изначально пустую базу.

Имена и пароль выше являются примером для локальной практики. Если используете
другие настройки, подставьте их в строку подключения.

### 3. Строка подключения

Создайте `.env` в корне проекта по образцу `.env.example`.
Если `.env` уже существует, отредактируйте его, сохранив свои настройки.

Для создания файла в macOS / Linux:

```bash
cp .env.example .env
```

В Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Укажите в `.env` строку подключения к своей учебной базе:

```dotenv
DATABASE_URL=postgresql://ticket_student:password@localhost:5432/ticket_booking_raw
```

Перед подключением `python-dotenv` загружает значения из `.env` в окружение
процесса, затем программа читает `DATABASE_URL` через `os.getenv()`.
Путь к `.env` определяется от расположения Python-файла, поэтому настройки
находятся и при запуске из другого каталога или из PyCharm.

Если `DATABASE_URL` уже задана в окружении терминала или конфигурации PyCharm,
она имеет приоритет над значением из `.env`. Например, для временного
переключения базы в macOS / Linux можно использовать `export DATABASE_URL='...'`,
а в PowerShell: `$env:DATABASE_URL = '...'`.

Файл `.env` содержит локальные секреты и исключен из Git. В репозиторий
добавляем только `.env.example` с примером настроек.

Если пароль содержит специальные символы URL, их нужно кодировать:
например, `@` записывается как `%40`.

На этапе ORM в строке подключения заменим имя базы на `ticket_booking_orm`.
Префикс `postgresql://` оставим общим для обеих версий; при создании движка
SQLAlchemy явно выберем драйвер Psycopg.

### 4. Проверка подключения

```bash
python -m ticket_booking.check_db
```

При успешном подключении:

```text
Подключение успешно. База: ticket_booking_raw, пользователь: ticket_student.
```

Команда выполняет только `SELECT current_database(), current_user`.
При отсутствии `DATABASE_URL` или ошибке подключения выводится сообщение
и программа завершается с кодом 1. При успехе код завершения равен 0.

### 5. Создание таблиц и демонстрационных данных

Убедитесь, что `DATABASE_URL` указывает на пустую базу `ticket_booking_raw`.
Из корня проекта откройте консоль Python:

```bash
python
```

Импортируйте функции и прочитайте настройки из `.env`:

```pycon
>>> from ticket_booking.config import get_database_url
>>> from ticket_booking.raw_sql.init_db import create_tables, seed_data
>>> database_url = get_database_url()
```

Создайте таблицы:

```pycon
>>> create_tables(database_url)
```

Затем отдельно добавьте демонстрационные данные:

```pycon
>>> seed_data(database_url)
```

После заполнения в базе будут 2 мероприятия, 12 мест и 1 билет.
Функции при успешном выполнении ничего не выводят.

Функции создают таблицы и записи внутри базы PostgreSQL. Сама база должна
быть создана на шаге 2. Версия ORM будет использовать свою базу и миграции Alembic.

В `init_db.py` за эти действия отвечают отдельные функции:

- `create_tables(database_url)` выполняет `ticket_booking/raw_sql/sql/schema.sql`.
- `seed_data(database_url)` выполняет
  `ticket_booking/raw_sql/sql/seed.sql`. В нем находятся все запросы заполнения.
  Связанные ID берутся из таблиц через `INSERT ... SELECT` и JOIN.

Каждая функция открывает собственное соединение через `with psycopg.connect(...)`
и выполняется в отдельной транзакции. Ошибка заполнения откатывает вставленные
данные, но ранее созданные таблицы сохраняются. `SERIAL` может пропускать номера
после отката, поэтому ID не задаются вручную и не предполагаются равными 1 и 2.
Подробнее: [транзакции Psycopg](https://www.psycopg.org/psycopg3/docs/basic/transactions.html).

Эти функции вызываем один раз при подготовке пустой учебной базы.
Ошибки выполнения SQL передаются вызывающему коду как исключения Psycopg.

В схеме ID объявлены как `SERIAL PRIMARY KEY`: PostgreSQL автоматически
генерирует целочисленные значения с помощью последовательности.
Подробнее: [тип SERIAL](https://www.postgresql.org/docs/current/datatype-numeric.html#DATATYPE-SERIAL).

Все даты в учебной модели храним как местное время одной площадки,
без часового пояса (`TIMESTAMP`). Расписание нескольких часовых поясов
в эту практику не входит.

### 6. Просмотр данных через SQL-клиент

Подключитесь к `ticket_booking_raw`. Проверьте количество записей:

```sql
SELECT COUNT(*) FROM events;  -- 2
SELECT COUNT(*) FROM seats;   -- 12
SELECT COUNT(*) FROM tickets; -- 1
```

Соедините три таблицы, чтобы увидеть, на какое мероприятие оформлен билет:

```sql
SELECT
    events.title,
    seats.row_number,
    seats.seat_number,
    tickets.customer_name
FROM tickets
JOIN seats ON seats.id = tickets.seat_id
JOIN events ON events.id = seats.event_id;
```

Результат: «Джазовый вечер», ряд 1, место 1, Анна Смирнова.

Ограничения схемы не позволяют повторить место внутри мероприятия,
дважды забронировать место или указать несуществующий внешний ключ.
Место с билетом нельзя удалить; удаление мероприятия с билетом также
будет отклонено. Мероприятие без билетов удаляется вместе со своими местами.
За это отвечают `UNIQUE`, `FOREIGN KEY`, `ON DELETE CASCADE` и `ON DELETE RESTRICT`.
Номера больше нуля и непустые строки проверяются через `CHECK`.
Подробнее: [ограничения PostgreSQL](https://www.postgresql.org/docs/current/ddl-constraints.html).

### 7. CRUD и поиск из консоли Python

После подготовки базы откройте консоль Python из корня проекта командой
`python`. Вызывайте функции отдельно:

```pycon
>>> from datetime import datetime
>>> from ticket_booking.config import get_database_url
>>> from ticket_booking.raw_sql import events, seats
>>> database_url = get_database_url()
>>> all_events = events.list_events(database_url)
>>> jazz_events = events.search_events(database_url, title_part="джаз")
>>> small_hall_events = events.search_events(database_url, venue_part="Малый")
>>> matching_events = events.find_events_by_seat(database_url, 1, 1)
>>> event_id = events.add_event(database_url, "Встреча с автором", "Малый зал", datetime(2026, 12, 1, 18, 0))
>>> seat_id = seats.add_seat(database_url, event_id, 1, 1)
>>> event_seats = seats.list_seats(database_url, event_id)
>>> seat = seats.find_seat(database_url, event_id, 1, 1)
>>> print(seat["row_number"], seat["seat_number"])
1 1
>>> events.update_event(database_url, event_id, "Встреча с писателем", "Малый зал", datetime(2026, 12, 1, 19, 0))
True
>>> seats.update_seat(database_url, seat_id, 1, 2)
True
>>> seats.delete_seat(database_url, seat_id)
True
>>> events.delete_event(database_url, event_id)
True
```

При поиске по названию и площадке оба условия применяются одновременно.
Пустая строка означает любое значение. `ILIKE` ищет без учета регистра;
`%` и `_` в поисковой строке имеют значение шаблонов SQL.
Поиск мероприятий по ряду и номеру учитывает и занятые места.
Для свободных мест есть отдельная функция `seats.list_free_seats()`.

Функции добавления возвращают ID новой записи, изменения и удаления – `True`,
если запись найдена, иначе `False`. Поиск одного места возвращает словарь
или `None`, выборки нескольких записей возвращают список словарей.
Для этого в запросах чтения используется `row_factory=dict_row`:
к полю обращаемся по имени, например `event["title"]`.
Подробнее: [результаты запросов Psycopg](https://www.psycopg.org/psycopg3/docs/advanced/rows.html).

Значения передаются вторым аргументом `cursor.execute()`, а в SQL обозначаются
через `%s`. В поиске f-строка формирует значение шаблона, которое тоже передается
отдельным параметром. Подробнее: [параметры запросов Psycopg](https://www.psycopg.org/psycopg3/docs/basic/params.html).

У мероприятия с билетами можно менять название и дату, но смена площадки
вызывает `ValueError`. Место с билетом нельзя редактировать.
Редактирование места меняет его ряд и номер в пределах текущего мероприятия.
При нарушении ограничений таблиц возникает исключение Psycopg.
Каждая операция выполняется в отдельной транзакции через `with`.

### 8. Бронирование и отмена

Из той же консоли Python можно создать отдельное мероприятие и пройти
цикл бронирования выбранного места:

```pycon
>>> from ticket_booking.raw_sql import tickets
>>> event_id = events.add_event(database_url, "Учебный концерт", "Малый зал", datetime(2026, 12, 2, 19, 0))
>>> seat_id = seats.add_seat(database_url, event_id, 1, 1)
>>> ticket_id = tickets.book_ticket(database_url, seat_id, "Анна Смирнова")
>>> seats.list_free_seats(database_url, event_id)
[]
>>> booked_tickets = tickets.list_tickets(database_url, event_id)
>>> print(booked_tickets[0]["customer_name"])
Анна Смирнова
>>> tickets.cancel_ticket(database_url, ticket_id)
True
>>> print(seats.list_free_seats(database_url, event_id)[0]["seat_number"])
1
>>> events.delete_event(database_url, event_id)
True
```

- `seats.list_free_seats(database_url, event_id)` находит места без билетов
  через `LEFT JOIN` и условие `tickets.id IS NULL`.
- `tickets.book_ticket(database_url, seat_id, customer_name)` добавляет билет
  и возвращает его ID. При повторном бронировании возникает `ValueError`
  с сообщением «Место уже забронировано.»
- `tickets.list_tickets(database_url, event_id)` возвращает список словарей
  с данными билета, покупателя, мероприятия и места через JOIN трех таблиц.
- `tickets.cancel_ticket(database_url, ticket_id)` удаляет билет и возвращает
  `True`; если билет не найден, возвращает `False`.

Предварительно проверять занятость для создания билета не требуется:
`UNIQUE (seat_id)` защищает от повторного бронирования, включая одновременные
запросы. В `book_ticket()` исключение `UniqueViolation` преобразуется в понятный
`ValueError` после выхода из `with`, когда транзакция уже откатилась.
После отмены билет удаляется, поэтому место снова попадает в список свободных.

## Учебные границы

Храним мероприятия, их пронумерованные места и действующие билеты.
Отмена бронирования удаляет билет и освобождает место. Одно и то же сочетание
ряда и номера может существовать у разных мероприятий.

В основную практику входят добавление, изменение, удаление и поиск мероприятий
и мест, просмотр свободных мест, бронирование и отмена. Поиск мероприятий
покажем по части названия, площадке и наличию конкретного ряда и номера места.

Оплату, регистрацию пользователей, временные брони и историю отмен оставим
за рамками занятия. Используем синхронный код и небольшие функции.
