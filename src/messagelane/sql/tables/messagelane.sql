DROP TABLE IF EXISTS message;
DROP TABLE IF EXISTS stream;

CREATE TABLE stream (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    marker BIGINT NOT NULL DEFAULT 0
);

CREATE TABLE message (
    id BIGSERIAL PRIMARY KEY,
    message_id UUID UNIQUE not NULL DEFAULT gen_random_uuid(), 
    stream_id BIGINT REFERENCES stream, 
    stream_position BIGINT not NULL,
    ts TIMESTAMPTZ not NULL DEFAULT now(),
    payload TEXT
);

CREATE INDEX IF NOT EXISTS stream_name_idx ON stream (name); 
CREATE INDEX IF NOT EXISTS message_message_id_idx ON message (message_id);
CREATE INDEX IF NOT EXISTS message_message_ts_idx ON message (ts);
CREATE INDEX IF NOT EXISTS message_message_stream_ts_idx ON message (stream_id, ts);


