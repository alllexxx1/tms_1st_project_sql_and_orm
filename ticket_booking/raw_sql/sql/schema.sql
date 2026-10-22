-- Схема создается в пустой учебной базе.
-- Транзакцией управляет Python-код в init_db.py.

CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    venue VARCHAR(150) NOT NULL,
    starts_at TIMESTAMP NOT NULL,

    CONSTRAINT ck_events_title_not_blank CHECK (btrim(title) <> ''),
    CONSTRAINT ck_events_venue_not_blank CHECK (btrim(venue) <> '')
);

CREATE TABLE seats (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL,
    row_number INTEGER NOT NULL,
    seat_number INTEGER NOT NULL,

    CONSTRAINT fk_seats_event FOREIGN KEY (event_id)
        REFERENCES events (id) ON DELETE CASCADE,
    CONSTRAINT ck_seats_row_positive CHECK (row_number > 0),
    CONSTRAINT ck_seats_number_positive CHECK (seat_number > 0),
    CONSTRAINT uq_seats_event_row_number UNIQUE (event_id, row_number, seat_number)
);

CREATE TABLE tickets (
    id SERIAL PRIMARY KEY,
    seat_id INTEGER NOT NULL,
    customer_name VARCHAR(100) NOT NULL,

    CONSTRAINT fk_tickets_seat FOREIGN KEY (seat_id)
        REFERENCES seats (id) ON DELETE RESTRICT,
    CONSTRAINT uq_tickets_seat UNIQUE (seat_id),
    CONSTRAINT ck_tickets_customer_not_blank CHECK (btrim(customer_name) <> '')
);
