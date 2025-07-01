-- :name del_message :affected

delete from message
where
    lane_id in (
        select id
        from lane
        where name = :name
        )
    and
    lane_position = :position 

