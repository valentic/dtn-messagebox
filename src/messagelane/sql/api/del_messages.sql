-- :name del_messages :affected

delete from message
where
    lane_id in (
        select id
        from lane
        where name like :name_pattern
        )
    and
    ts <= :ts

