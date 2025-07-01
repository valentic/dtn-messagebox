DROP TABLE IF EXISTS message;
DROP TABLE IF EXISTS lane;

CREATE TABLE lane (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    marker BIGINT NOT NULL DEFAULT 0
);

CREATE TABLE message (
    id BIGSERIAL PRIMARY KEY,
    message_id UUID UNIQUE not NULL DEFAULT gen_random_uuid(), 
    lane_id BIGINT REFERENCES lane, 
    lane_position BIGINT not NULL,
    ts TIMESTAMPTZ not NULL DEFAULT now(),
    payload TEXT
);

CREATE INDEX IF NOT EXISTS lane_name_idx ON lane (name); 
CREATE INDEX IF NOT EXISTS message_message_id_idx ON message (message_id);
CREATE INDEX IF NOT EXISTS message_message_ts_idx ON message (ts);
CREATE INDEX IF NOT EXISTS message_message_lane_ts_idx ON message (lane_id, ts);


