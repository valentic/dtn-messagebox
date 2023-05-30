DROP TABLE IF EXISTS messagebox;
DROP TABLE IF EXISTS stream;
--DROP EXTENSION IF EXISTS "uuid-ossp";

--CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE stream (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    marker BIGINT NOT NULL DEFAULT 0
);

CREATE TABLE messagebox (
    id BIGSERIAL PRIMARY KEY,
    --message_id UUID UNIQUE not NULL DEFAULT uuid_generate_v4(), 
    message_id UUID UNIQUE not NULL DEFAULT gen_random_uuid(), 
    stream_id BIGINT REFERENCES stream, 
    stream_position BIGINT not NULL,
    ts TIMESTAMPTZ not NULL DEFAULT now(),
    payload TEXT
);

CREATE INDEX IF NOT EXISTS stream_name_idx ON stream (name); 
CREATE INDEX IF NOT EXISTS messagebox_message_id_idx ON messagebox (message_id);
CREATE INDEX IF NOT EXISTS messagebox_message_ts_idx ON messagebox (ts);
CREATE INDEX IF NOT EXISTS messagebox_message_stream_ts_idx ON messagebox (stream_id, ts);


