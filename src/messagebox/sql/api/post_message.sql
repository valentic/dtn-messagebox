-- :name post_message :insert

with cte as (
    update stream
        set marker = marker+1
        where name = :name
    returning *
)
insert into messagebox(stream_id, stream_position, ts, payload)
select cte.id, cte.marker, :ts, :payload from cte


