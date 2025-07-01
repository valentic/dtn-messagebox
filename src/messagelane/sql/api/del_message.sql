-- :name del_message :affected

delete from message
where
    stream_id in (
        select id
        from stream
        where name = :name
        )
    and
    stream_position = :position 

