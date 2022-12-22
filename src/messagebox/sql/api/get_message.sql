-- :name get_message :one

select
    stream.name as stream,
    stream_position,
    ts,
    message_id,
    payload
from
    messagebox as mb
join
    stream on stream_id = stream.id
where
    stream.name = :name
    and
    stream_position = :position
