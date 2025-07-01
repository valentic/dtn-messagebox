-- :name post_message :insert

with cte as (
    update lane
        set marker = marker+1
        where name = :name
    returning *
)
insert into message(lane_id, lane_position, ts, payload)
select cte.id, cte.marker, :ts, :payload from cte


