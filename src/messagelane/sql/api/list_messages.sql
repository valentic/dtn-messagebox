-- :name list_messages :many

select
    lane.name,
    lane_position,
    ts,
    message_id
from
    message as mb
join
    lane on mb.lane_id = lane.id
where
    lane.name = :name
order by
    lane_position
