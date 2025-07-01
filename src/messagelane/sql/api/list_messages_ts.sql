-- :name list_messages_ts :many

select
    stream.name as stream,
    stream_position,
    ts,
    message_id
from
    message as mb
join
    stream on mb.stream_id = stream.id
where
    stream.name = :name
    and
    ts >= :ts
order by
    stream_position
