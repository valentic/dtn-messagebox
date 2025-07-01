-- :name del_message_range :affected

delete from message
where
    stream_id in (
        select id
        from stream
        where name = :name
        )
    and
    stream_position between :start and :stop

