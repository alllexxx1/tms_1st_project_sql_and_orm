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
из консоли Python. Для ORM подготовлены модели, первая миграция Alembic
и заполнение примерами. CRUD и бронирование через ORM добавим следующим чанком.
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

Для ORM используем `DeclarativeBase`, `Mapped`,
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

Для ORM замените имя базы в строке подключения на `ticket_booking_orm`.
Префикс `postgresql://` остается общим для обеих версий; функция `get_engine()`
явно выбирает драйвер Psycopg через `postgresql+psycopg`.

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

Каждая функция использует `with get_cursor(...)` и выполняется в отдельной
транзакции. Общий контекстный менеджер открывает соединение и курсор.
Ошибка заполнения откатывает вставленные
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

### 9. Общий контекстный менеджер

Повторяющийся код открытия соединения и курсора вынесен в
`ticket_booking/raw_sql/database.py`. Теперь в функциях достаточно одного `with`:

```python
from ticket_booking.raw_sql.database import get_cursor

with get_cursor(database_url) as cursor:
    cursor.execute("SELECT id, title FROM events")
    rows = cursor.fetchall()
```

`get_cursor()` использует `@contextmanager` из стандартного модуля `contextlib`.
Код до `yield cursor` открывает ресурсы и передает курсор вызывающему коду.
При выходе из его блока `with` управление возвращается в менеджер:
вложенные контексты Psycopg закрывают курсор, сохраняют транзакцию при успехе
или откатывают ее при исключении и закрывают соединение.

По умолчанию строки возвращаются как кортежи. Для словарей передаем
`get_cursor(database_url, row_factory=dict_row)`, как в функциях поиска.
Каждый вызов по-прежнему создает отдельное соединение и транзакцию.
Время установления соединения ограничено пятью секундами.

### 10. Модели SQLAlchemy

Модели находятся в `ticket_booking/orm/models.py`: `Event`, `Seat`, `Ticket`.
Каждый класс описывает таблицу, а его экземпляр представляет запись.
Используем современный декларативный стиль SQLAlchemy:

- `Base(DeclarativeBase)` хранит общее описание таблиц в `Base.metadata`.
- `Mapped[int]`, `Mapped[str]`, `Mapped[datetime]` задают типы полей.
  Без `None` в аннотации колонка получает `NOT NULL`.
- `mapped_column()` задает параметры колонки: например, первичный ключ
  или ограничение длины строки. Целочисленный `primary_key=True` в нашей
  схеме PostgreSQL создает `SERIAL`.
- `ForeignKey`, `CheckConstraint`, `UniqueConstraint` описывают те же
  ограничения, что и в `schema.sql`.
- `relationship()` позволяет переходить между объектами: `event.seats`,
  `seat.event`, `seat.ticket`, `ticket.seat`. Связь `Seat.ticket` допускает `None`,
  поскольку у свободного места нет билета; колонка `tickets.seat_id` обязательна.
- `back_populates` связывает два направления отношения. `passive_deletes="all"`
  оставляет удаление связей базе данных: сохраняются правила `CASCADE` и `RESTRICT`.

Подробнее: [модели и Session](https://docs.sqlalchemy.org/en/21/orm/quickstart.html),
[удаление связанных объектов](https://docs.sqlalchemy.org/en/21/orm/cascades.html#passive-deletes).

### 11. Первая миграция Alembic

Обновите зависимости:

```bash
python -m pip install -r requirements.txt
```

Переключите `DATABASE_URL` в `.env` на изначально пустую базу `ticket_booking_orm`.
Если переменная уже задана в окружении терминала или PyCharm, обновите и ее:
она имеет приоритет над `.env`.

```dotenv
DATABASE_URL=postgresql://ticket_student:password@localhost:5432/ticket_booking_orm
```

Миграции создают таблицы; базу PostgreSQL предварительно создайте на шаге 2.
При работе с ORM таблицы создаем через Alembic. Заполняем их отдельной функцией
`seed_data()` после применения миграции.

В проекте уже есть настроенное окружение Alembic:

- `alembic.ini` задает каталог миграций и вывод сообщений.
- `migrations/env.py` получает подключение из `.env` и описание таблиц
  из `Base.metadata`.
- `migrations/versions/0001_create_ticket_tables.py` содержит первую миграцию:
  `upgrade()` создает три таблицы, `downgrade()` удаляет их в обратном порядке.
- `migrations/script.py.mako` служит шаблоном новых миграций.

На уроке создаем и применяем миграцию вручную, выполняя каждый шаг в терминале.
Для воспроизведения этого этапа начинаем с версии проекта перед добавлением
ORM (коммит `6d2c5bf`), затем пишем модели и настраиваем Alembic.

1. Создаем стандартное окружение Alembic из корня проекта:

   ```bash
   python -m alembic init migrations
   ```

2. Разбираем созданные файлы и настраиваем пути в `alembic.ini`.
   Строку подключения получаем из `.env` через общий `get_database_url()`.

3. Редактируем `migrations/env.py`: импортируем `Base` из ORM-моделей
   и задаем `target_metadata = Base.metadata`. Для подключения используем
   `get_engine(get_database_url())`. Пример итоговой настройки находится
   в [migrations/env.py](migrations/env.py).

4. Генерируем первую миграцию по написанным моделям:

   ```bash
   python -m alembic revision --autogenerate --rev-id 0001 -m "create ticket tables"
   ```

5. Открываем созданный файл в `migrations/versions/` и просматриваем
   `upgrade()` и `downgrade()`: порядок таблиц, поля, внешние ключи,
   проверки и уникальность. Генерация файла еще не применяет миграцию к базе.

6. Отдельно применяем миграцию и проверяем результат:

   ```bash
   python -m alembic upgrade head
   python -m alembic current
   python -m alembic check
   ```

`upgrade head` применяет миграции, `current` показывает текущую версию (`0001`),
`check` проверяет, видит ли Alembic изменения схемы относительно моделей.
В базе также появится служебная таблица `alembic_version`.

В готовом репозитории окружение и миграция уже сохранены как результат этих
шагов. Для запуска этой версии достаточно выполнить:

```bash
python -m alembic upgrade head
python -m alembic current
python -m alembic check
```

Повторять `init` и генерацию первой миграции в готовой версии не требуется.
Подробнее: [руководство Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html),
[автоматическая генерация](https://alembic.sqlalchemy.org/en/latest/autogenerate.html).

### 12. Движок, Session и заполнение через ORM

После применения миграции откройте консоль Python:

```pycon
>>> from ticket_booking.config import get_database_url
>>> from ticket_booking.orm.database import get_engine
>>> from ticket_booking.orm.init_db import seed_data
>>> engine = get_engine(get_database_url())
>>> seed_data(engine)
```

`get_engine()` создает движок SQLAlchemy. Само создание движка не устанавливает
соединение: оно потребуется при первом обращении к базе. Движок можно один раз
создать в консоли и передавать в ORM-функции.

`seed_data()` вызываем один раз на пустых таблицах. Функция создает объекты
двух мероприятий, 12 мест и одного билета. Связи задаются через атрибуты
`seats` и `ticket`; SQLAlchemy самостоятельно подставляет внешние ключи.
`session.add_all()` добавляет объекты в сессию, `session.commit()` сохраняет
их в базе. Блок `with Session(engine)` закрывает сессию; сохранение изменений
в этом примере выполняет явный `commit()`.

Проверим записи и связи:

```pycon
>>> from sqlalchemy import select
>>> from sqlalchemy.orm import Session
>>> from ticket_booking.orm.models import Event, Seat, Ticket
>>> with Session(engine) as session:
...     ticket = session.scalars(select(Ticket)).one()
...     print(ticket.customer_name)
...     print(ticket.seat.event.title)
...     print(ticket.seat.row_number, ticket.seat.seat_number)
...
Анна Смирнова
Джазовый вечер
1 1
>>> engine.dispose()
```

`select(Ticket)` описывает запрос, `session.scalars()` получает объекты модели,
а `one()` ожидает ровно один результат. Связанные объекты читаем внутри открытой
сессии. `engine.dispose()` освобождает оставшиеся соединения движка при завершении работы.

## Учебные границы

Храним мероприятия, их пронумерованные места и действующие билеты.
Отмена бронирования удаляет билет и освобождает место. Одно и то же сочетание
ряда и номера может существовать у разных мероприятий.

В основную практику входят добавление, изменение, удаление и поиск мероприятий
и мест, просмотр свободных мест, бронирование и отмена. Поиск мероприятий
покажем по части названия, площадке и наличию конкретного ряда и номера места.

Оплату, регистрацию пользователей, временные брони и историю отмен оставим
за рамками занятия. Используем синхронный код и небольшие функции.
