-- :name del_messages :affected

delete from message
where
    stream_id in (
        select id
        from stream
        where name like :name_pattern
        )
    and
    ts <= :ts

