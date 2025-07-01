-- :name overview :many

select
    lane.name as lane,
    coalesce(min(lane_position),0) as min_position,
    coalesce(max(lane_position),0) as max_position,
    count(lane_position) as count,
    min(ts) as min_ts,
    max(ts) as max_ts
from
    lane
left join lateral (
    select *
        from message as mb
        where lane_id = lane.id
        order by ts
    ) as messages on true
group by
    lane.id
order by
    lane.name
