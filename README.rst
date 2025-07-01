MessageLane 
===========

An experiment in using a SQL database as a usenet-like server.


Command Line Usage
------------------

mlctl --help
    Show options 

mlctl overview 
    Display a table of all messages

mlctl stream list
    List all stream names
    
mlctl stream create <stream_name>
    Create a new stream
    
mlctl stream del <stream_name>
    Delete a stream

mlctl messages new <stream_name> <ts>
    List messages in stream since ts
    
mlctl messages list <stream_name>
    List all messages (times/position/id) in stream

mlctl messages del <stream_name> <ts>
    Delete messages in stream older than ts

mlctl message get <stream_name> <position>
    Retrieve message from stream at position

mlctl message get-next <stream_name> <position>
    Retrieve the next message from stream at position
    
mlctl message post <stream_name> <filename>
    Post the contents of filename to a stream
    
mlctl message del <stream_name> <position> [end_position]
    Delete a message or range of messages from a stream

mlctl message has <id> 
    Test if message id is in database 


Python API
----------

has_stream(name)
    Test if stream exists

get_stream(name)
    Return stream entry

overview()
    Return summary overview

list_streams()
    List streams

create_stream(name)
    Create a new stream

del_stream(name)
    Delete a new stream

list_messages(name)
    List messages in a stream

list_messages_ts(name, ts)
    List new messages since ts

del messages(name_pattern, ts)
    Delete from multiple streams since ts

get_message(name, position)
    Return a message from a stream

get_next_message(name, position)
    Return the next message from a stream

post_message(name, msg)
    Post a message to a stream

del_message(name, position)
    Delete a message from stream

del_message_range(name, start_position, end_position)
    Delete a range of messages from a stream

has_message(id)
    Check if message id exists 



