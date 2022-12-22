-- :name get_stream :one

select * from stream where name = :name limit 1
