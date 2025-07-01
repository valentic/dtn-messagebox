-- :name get_next_message :one

select
    lane.name as lane,
    lane_position,
    ts,
    message_id,
    payload
from
    message as mb
join
    lane on lane_id = lane.id
where
    lane.name = :name
    and
    lane_position > :position
limit 1
