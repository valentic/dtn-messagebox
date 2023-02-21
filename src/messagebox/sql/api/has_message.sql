-- :name has_message :one

select * from messagebox where message_id=:message_id limit 1
