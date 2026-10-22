-- Выполняется функцией seed_data() один раз для пустых таблиц.

INSERT INTO events (title, venue, starts_at)
VALUES
    ('Джазовый вечер', 'Малый зал', '2026-11-15 19:00:00'),
    ('Лекция о космосе', 'Большой зал', '2026-11-16 18:00:00');

-- Каждый запрос добавляет одно и то же место на оба мероприятия.
-- ID мероприятий берем из таблицы, а не задаем числами 1 и 2.
INSERT INTO seats (event_id, row_number, seat_number)
SELECT id, 1, 1 FROM events;

INSERT INTO seats (event_id, row_number, seat_number)
SELECT id, 1, 2 FROM events;

INSERT INTO seats (event_id, row_number, seat_number)
SELECT id, 1, 3 FROM events;

INSERT INTO seats (event_id, row_number, seat_number)
SELECT id, 2, 1 FROM events;

INSERT INTO seats (event_id, row_number, seat_number)
SELECT id, 2, 2 FROM events;

INSERT INTO seats (event_id, row_number, seat_number)
SELECT id, 2, 3 FROM events;

-- Находим нужное место по мероприятию, ряду и номеру.
INSERT INTO tickets (seat_id, customer_name)
SELECT seats.id, 'Анна Смирнова'
FROM seats
JOIN events ON events.id = seats.event_id
WHERE events.title = 'Джазовый вечер'
    AND seats.row_number = 1
    AND seats.seat_number = 1;
