-- :name overview :many

select
    stream.name as stream,
    coalesce(min(stream_position),0) as min_position,
    coalesce(max(stream_position),0) as max_position,
    count(stream_position) as count,
    min(ts) as min_ts,
    max(ts) as max_ts
from
    stream
left join lateral (
    select *
    from messagebox as mb
    where stream_id = stream.id
    order by ts
    ) as messages on true
group by
    stream.id
order by
    stream.name
