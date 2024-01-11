-- :name has_message :one

select * from message where message_id=:message_id limit 1
