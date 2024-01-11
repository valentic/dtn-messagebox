-- :name list_messages :many

select
    stream.name,
    stream_position,
    ts,
    message_id
from
    message as mb
join
    stream on mb.stream_id = stream.id
where
    stream.name = :name
order by
    stream_position
