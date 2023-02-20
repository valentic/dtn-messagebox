Message Box
===========

An experiment in using a SQL database as a usenet-like server.


Command Line Usage
------------------

mbctl --help
    Show options 

mbctl overview 
    Display a table of all messages

mbctl stream list
    List all stream names
    
mbctl stream create <stream_name>
    Create a new stream
    
mbctl stream del <stream_name>
    Delete a stream

mbctl messages new <stream_name> <ts>
    List messages in stream since ts
    
mbctl messages list <stream_name>
    List all messages (times/position/id) in stream

mbctl messages del <stream_name> <ts>
    Delete messages in stream older than ts

mbctl message get <stream_name> <position>
    Retrieve message from stream at position

mbctl message get-next <stream_name> <position>
    Retrieve the next message from stream at position
    
mbctl message post <stream_name> <filename>
    Post the contents of filename to a stream
    
mbctl message del <stream_name> <position> [end_position]
    Delete a message or range of messages from a stream



