CREATE TYPE user_status AS ENUM ('pending', 'approved', 'rejected');

CREATE TABLE users (
    id          BIGSERIAL PRIMARY KEY,
    email       TEXT NOT NULL UNIQUE,
    name        TEXT,
    picture     TEXT,
    status      user_status NOT NULL DEFAULT 'pending',
    is_admin    BOOLEAN NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ
);

-- Admin pré-aprovado; idempotente via ON CONFLICT
INSERT INTO users (email, name, status, is_admin)
VALUES ('lbarretti@gmail.com', 'Leonardo', 'approved', TRUE)
ON CONFLICT (email) DO UPDATE SET is_admin = TRUE, status = 'approved';
