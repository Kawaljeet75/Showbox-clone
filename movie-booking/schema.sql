-- schema.sql
CREATE TABLE IF NOT EXISTS users (
  id          INTEGER   PRIMARY KEY AUTOINCREMENT,
  username    TEXT      NOT NULL UNIQUE,
  password    TEXT      NOT NULL,
  email       TEXT      NOT NULL UNIQUE,
  role        TEXT      DEFAULT 'user',
  created_at  DATETIME  DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS movies (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  title        TEXT    NOT NULL,
  description  TEXT,
  showtime     TEXT,
  genre        TEXT,
  rating       REAL,
  poster_url   TEXT,
  trailer_url  TEXT,
  duration     TEXT,
  language     TEXT,
  release_date TEXT,
  age_rating   TEXT,
  director     TEXT,
  starring     TEXT
);

CREATE TABLE IF NOT EXISTS bookings (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  movie_id  INTEGER NOT NULL,
  show_date TEXT    NOT NULL,
  show_time TEXT    NOT NULL,
  seat_no   TEXT    NOT NULL,
  booked_at TEXT    NOT NULL,
  FOREIGN KEY(movie_id) REFERENCES movies(id)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_seat
  ON bookings(movie_id, show_date, show_time, seat_no);
