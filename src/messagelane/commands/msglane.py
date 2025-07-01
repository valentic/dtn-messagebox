#!/usr/bin/env python
"""MessageLane control program"""

##########################################################################
#
#   MessageLane command line interface
#
#   2022-12-16  Todd Valentic
#               Initial implementation
#
#   2024-01-06  Todd Valentic
#               Updated for sqlalchemy 2 
#
#   2025-07-01  Todd Valentic
#               Convert to MessageLane
#
##########################################################################

from datetime import datetime, timezone
import functools
import sys
import uuid

import click
import prefixed
import texttable as tt

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import messagelane

# Utility functions ------------------------------------------------------


def format_ts(ts):
    """Format datetime"""

    if not ts:
        return ""

    return ts.strftime("%Y-%m-%d %H:%M:%S")

def format_bytes(num):
    """Format bytes"""

    if num is None:
        return ""

    return f"{prefixed.Float(num):!.2h}B"
    

def as_datetime(ts):
    """Datetime from ISO string"""

    dt = datetime.fromisoformat(ts)

    if not dt.tzinfo:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt

def values(result, keys):
    """Return values for keys in result"""

    return [getattr(result, key) for key in keys]

class ContextObject:

    def __init__(self, session):
        self.session = session
        self.msglane = messagelane.MessageLane(session)

def pass_msglane(func):
    @click.pass_obj
    @functools.wraps(func)
    def wrapper(opt, *args, **kw):
        func(opt.msglane, *args, **kw)
    return wrapper

# Base commands ---------------------------------------------------------


@click.group()
@click.option("--database", envvar="MESSAGEBOX_URL", default="postgresql:///messagelane")
@click.option("--debug/--no-debug", envvar="MESSAGEBOX_DEBUG", default=False)
@click.pass_context
def cli(ctx, database, debug):
    """Base command group"""

    engine = create_engine(database, echo=debug)
    session = ctx.with_resource(sessionmaker(engine).begin())
    ctx.obj = ContextObject(session) 

@cli.command()
@click.option("--as_bytes/--no-as_bytes", default=False, help="Display size as bytes")
@pass_msglane
def overview(msglane, as_bytes):
    """MessageLane overview"""

    results = msglane.overview()

    tb = tt.Texttable()

    tb.set_deco(tb.HEADER)

    if as_bytes:
        format_size = "i"
    else:
        format_size = format_bytes

    tb.header(["Stream", "Min", "Max", "Count", "Start (UTC)", "Stop (UTC)", "Total Size"])
    tb.set_cols_dtype(["t", "i", "i", "i", format_ts, format_ts, format_size])
    tb.set_cols_align(["l", "r", "r", "r", "c", "c", "r"])
    tb.set_header_align(["c", "r", "r", "r", "c", "c", "c"])
    tb.set_max_width(0)

    for result in results:
        tb.add_row(result.values())

    click.echo(tb.draw())

@cli.command()
@click.option("--as_bytes/--no-as_bytes", default=False, help="Display size as bytes")
@pass_msglane
def status(msglane, as_bytes):
    """MessageLane status"""

    results = msglane.status()

    if as_bytes:
        format_size = "i"
    else:
        format_size = format_bytes

    # Database table

    dbtb = tt.Texttable()

    dbtb.set_deco(tt.Texttable.HEADER)

    dbtb.header(["Database", "Size"])
    dbtb.set_cols_dtype(["t", format_size])
    dbtb.set_cols_align(["l", "r"])
    dbtb.set_header_align(["c", "c"])
    #dbtb.set_max_width(0)

    dbtb.add_row([results["database"]["name"], results["database"]["size"]])

    # Tables table

    tb = tt.Texttable()

    tb.set_deco(tt.Texttable.HEADER)

    tb.header(["Table", "Rows", "Size"])
    tb.set_cols_dtype(["t", "i", format_size])
    tb.set_cols_align(["l", "r", "r"])
    tb.set_header_align(["c", "c", "c"])
    tb.set_max_width(0)

    for table, info in results["table"].items():
        tb.add_row([table, info["rows"], info["size"]])

    # Index table

    ixtb = tt.Texttable()

    ixtb.set_deco(tt.Texttable.HEADER)

    ixtb.header(["Table", "Index", "Size"])
    ixtb.set_cols_dtype(["t", "t", format_size])
    ixtb.set_cols_align(["l", "l", "r"])
    ixtb.set_header_align(["c", "c", "c"])
    ixtb.set_max_width(0)

    for table, index_results in results["index"].items():
        for index, size in index_results.items():
            ixtb.add_row([table, index, size])

    # Display

    click.echo()
    click.echo(dbtb.draw())
    click.echo()
    click.echo(tb.draw())
    click.echo()
    click.echo(ixtb.draw())
    click.echo()



# Stream commands --------------------------------------------------------


@cli.group()
def stream():
    """Stream command group"""



@stream.command("list")
@pass_msglane
def list_streams(msglane):
    """List stream names"""

    results = msglane.list_streams()

    tb = tt.Texttable()

    tb.set_deco(tb.HEADER)

    tb.header(["Stream"])
    tb.set_cols_dtype(["t"])
    tb.set_cols_align(["l"])
    tb.set_header_align(["c"])
    tb.set_max_width(0)

    for result in results:
        tb.add_row(values(result, ["name"]))

    click.echo(tb.draw())


@stream.command("create")
@click.argument("name")
@pass_msglane
def create_stream(msglane, name):
    """Create a new stream"""

    if msglane.has_stream(name):
        click.echo("The stream already exists")
        return

    msglane.create_stream(name)

    click.echo(f"Created stream {name}")


@stream.command("del")
@click.argument("name")
@pass_msglane
def del_stream(msglane, name):
    """Delete a stream"""

    if not msglane.has_stream(name):
        click.echo("The stream does not exist")
        return

    msglane.del_stream(name)

    click.echo(f"Removed stream {name}")


# Messages commands ------------------------------------------------------


@cli.group()
def messages():
    "Messages command group" ""


@messages.command("list")
@click.argument("name")
@click.option("--as_bytes/--no-as_bytes", default=False, help="Display size as bytes")
@pass_msglane
def list_messages(msglane, name, as_bytes):
    """List messages in a stream"""

    if not msglane.has_stream(name):
        click.echo("The stream does not exist")
        return

    results = msglane.list_messages(name)

    tb = tt.Texttable()

    tb.set_deco(tb.HEADER)

    format_size = "i" if as_bytes else format_bytes

    tb.header(["Stream", "Position", "Timestamp (UTC)", "Size", "Message UUID"])
    tb.set_cols_dtype(["t", "i", format_ts, format_size, "t"])
    tb.set_cols_align(["l", "r", "l", "r", "l"])
    tb.set_header_align(["c", "r", "c", "c", "c"])
    tb.set_max_width(0)

    for result in results:
        tb.add_row([
            result.stream.name,
            result.stream_position,
            result.ts,
            result.payload_size,
            result.message_uuid
            ])
            
    click.echo(tb.draw())


@messages.command("new")
@click.argument("name")
@click.argument("ts")
@pass_msglane
def new_messages(msglane, name, ts):
    """List new messages in a stream"""

    if not msglane.has_stream(name):
        click.echo("The stream does not exist")
        return

    dt = as_datetime(ts) 

    results = msglane.list_messages_ts(name, dt)

    tb = tt.Texttable()

    tb.set_deco(tb.HEADER)

    tb.header(["Stream", "Position", "Timestamp (UTC)", "Message ID"])
    tb.set_cols_dtype(["t", "i", format_ts, "t"])
    tb.set_cols_align(["l", "r", "l", "l"])
    tb.set_header_align(["c", "r", "c", "c"])
    tb.set_max_width(0)

    for result in results:
        tb.add_row(result.values())

    click.echo(tb.draw())


@messages.command("del")
@click.argument("name")
@click.argument("ts")
@pass_msglane
def del_messages(msglane, name, ts):
    """Delete old messages"""

    dt = as_datetime(ts)

    result = msglane.del_messages(name, dt)
    click.echo(result)

# Single message commands ------------------------------------------------


@cli.group()
def message():
    """Single message command group"""


@message.command("get")
@click.argument("name")
@click.argument("position", type=int)
@pass_msglane
def get_message(msglane, name, position):
    """Return a message at a given position in a stream"""

    if not msglane.has_stream(name):
        click.echo("The stream does not exist")
        return

    result = msglane.get_message(name, position)

    if result:
        click.echo(result.payload)
    else:
        click.echo("No message found")

@message.command("uuid")
@click.argument("message_uuid", type=uuid.UUID)
@pass_msglane
def get_message_from_uuid(msglane, message_uuid):
    """Return a message with given uuid""" 

    result = msglane.get_message_from_uuid(message_uuid)

    if result:
        click.echo(result.payload)
    else:
        click.echo("No message found")


@message.command("next")
@click.argument("name")
@click.argument("position", type=int)
@pass_msglane
def next_message(msglane, name, position):
    """Return the next message from a stream"""

    if not msglane.has_stream(name):
        click.echo("The stream does not exist")
        return

    result = msglane.next_message(name, position)

    if result:
        click.echo(result.stream_position)
    else:
        click.echo("At end, no more messages")

@message.command("first")
@click.argument("name")
@pass_msglane
def first_message(msglane, name):
    """Return the first message from a stream"""

    if not msglane.has_stream(name):
        click.echo("The stream does not exist")
        return

    result = msglane.first_message(name)

    if result:
        click.echo(result.stream_position)
    else:
        click.echo("No messages found")

@message.command("post")
@click.argument("name")
@click.argument("payload_filename")
@pass_msglane
def post_message(msglane, name, payload_filename):
    """Post a new message to a stream"""

    if not msglane.has_stream(name):
        click.echo("The stream does not exist")
        return

    result = msglane.post_message_from_file(name, payload_filename)

    click.echo(result)

@message.command("forward")
@click.argument("name")
@click.argument("ts", type=datetime.fromisoformat)
@click.argument("message_uuid", type=uuid.UUID)
@click.argument("payload_filename")
@pass_msglane
def post_message(msglane, name, ts, message_uuid, payload_filename):
    """Post an existing message to a stream"""

    if not msglane.has_stream(name):
        click.echo("The stream does not exist")
        return

    result = msglane.post_message_from_file(name, payload_filename, ts=ts, message_uuid=message_uuid)

    click.echo(result)



@message.command("del")
@click.argument("name")
@click.argument("position", type=int)
@click.argument("endposition", required=False, type=int)
@pass_msglane
def del_message(msglane, name, position, endposition):
    """Delete a messages from a stream""" 

    if not msglane.has_stream(name):
        click.echo("The stream does not exist")
        return

    if endposition:
        msglane.del_message_range(name, position, endposition)
        click.echo(f"Deleted messages from {name}:{position}-{endposition}")
    else:
        msglane.del_message(name, position)
        click.echo(f"Deleted message at {name}:{position}")

@message.command("has")
@click.argument("message_uuid", type=uuid.UUID)
@pass_msglane
def has_message(msglane, message_uuid):
    """Check if a message with message_uuid exists""" 

    result = msglane.has_message(message_uuid)

    if result:
        click.echo('True')
    else:
        click.echo('False')
        sys.exit(1) 

def main():
    """Main command starting point"""

    cli()
