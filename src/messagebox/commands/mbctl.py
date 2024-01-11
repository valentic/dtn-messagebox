#!/usr/bin/env python
"""MessageBox control program"""

##########################################################################
#
#   MessageBox command line interface
#
#   2022-12-16  Todd Valentic
#               Initial implementation
#
#   2024-01-06  Todd Valentic
#               Updated for sqlalchemy 2 
#
##########################################################################

import datetime
import functools
import sys
import uuid

import click
import texttable as tt

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import messagebox

# Utility functions ------------------------------------------------------


def format_ts(ts):
    """Format datetime"""

    if not ts:
        return ""

    return ts.strftime("%Y-%m-%d %H:%M:%S")

def as_datetime(ts):
    """Datetime from ISO string"""

    dt = datetime.datetime.fromisoformat(ts)

    if not dt.tzinfo:
        dt = dt.replace(tzinfo=datetime.timezone.utc)

    return dt

def values(result, keys):
    """Return values for keys in result"""

    return [getattr(result, key) for key in keys]

class ContextObject:

    def __init__(self, session):
        self.session = session
        self.mb = messagebox.MessageBox(session)

def pass_mb(func):
    @click.pass_obj
    @functools.wraps(func)
    def wrapper(opt, *args, **kw):
        func(opt.mb, *args, **kw)
    return wrapper

# Base commands ---------------------------------------------------------


@click.group()
@click.option("--database", envvar="MESSAGEBOX_URL", default="postgresql:///messagebox2")
@click.option("--debug/--no-debug", envvar="MESSAGEBOX_DEBUG", default=False)
@click.pass_context
def cli(ctx, database, debug):
    """Base command group"""

    engine = create_engine(database, echo=debug)
    session = ctx.with_resource(sessionmaker(engine).begin())
    ctx.obj = ContextObject(session) 

@cli.command()
@pass_mb
def overview(mb):
    """MessageBox overview"""

    results = mb.overview()

    tb = tt.Texttable()

    tb.set_deco(tb.HEADER)

    tb.header(["Stream", "Min", "Max", "Count", "Start (UTC)", "Stop (UTC)"])
    tb.set_cols_dtype(["t", "i", "i", "i", format_ts, format_ts])
    tb.set_cols_align(["l", "r", "r", "r", "c", "c"])
    tb.set_header_align(["c", "r", "r", "r", "c", "c"])
    tb.set_max_width(0)

    for result in results:
        tb.add_row(result.values())

    click.echo(tb.draw())


# Stream commands --------------------------------------------------------


@cli.group()
def stream():
    """Stream command group"""



@stream.command("list")
@pass_mb
def list_streams(mb):
    """List stream names"""

    results = mb.list_streams()

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
@pass_mb
def create_stream(mb, name):
    """Create a new stream"""

    if mb.has_stream(name):
        click.echo("The stream already exists")
        return

    mb.create_stream(name)

    click.echo(f"Created stream {name}")


@stream.command("del")
@click.argument("name")
@pass_mb
def del_stream(mb, name):
    """Delete a stream"""

    if not mb.has_stream(name):
        click.echo("The stream does not exist")
        return

    mb.del_stream(name)

    click.echo(f"Removed stream {name}")


# Messages commands ------------------------------------------------------


@cli.group()
def messages():
    "Messages command group" ""


@messages.command("list")
@click.argument("name")
@pass_mb
def list_messages(mb, name):
    """List messages in a stream"""

    if not mb.has_stream(name):
        click.echo("The stream does not exist")
        return

    results = mb.list_messages(name)

    tb = tt.Texttable()

    tb.set_deco(tb.HEADER)

    tb.header(["Stream", "Position", "Timestamp (UTC)", "Message UUID"])
    tb.set_cols_dtype(["t", "i", format_ts, "t"])
    tb.set_cols_align(["l", "r", "l", "l"])
    tb.set_header_align(["c", "r", "c", "c"])
    tb.set_max_width(0)

    for result in results:
        tb.add_row([
            result.stream.name,
            result.stream_position,
            result.ts,
            result.message_uuid
            ])
            
    click.echo(tb.draw())


@messages.command("new")
@click.argument("name")
@click.argument("ts")
@pass_mb
def new_messages(mb, name, ts):
    """List new messages in a stream"""

    if not mb.has_stream(name):
        click.echo("The stream does not exist")
        return

    dt = as_datetime(ts) 

    results = mb.list_messages_ts(name, dt)

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
@pass_mb
def del_messages(mb, name, ts):
    """Delete old messages"""

    dt = as_datetime(ts)

    result = mb.del_messages(name, dt)
    click.echo(result)

# Single message commands ------------------------------------------------


@cli.group()
def message():
    """Single message command group"""


@message.command("get")
@click.argument("name")
@click.argument("position", type=int)
@pass_mb
def get_message(mb, name, position):
    """Return a message at a given position in a stream"""

    if not mb.has_stream(name):
        click.echo("The stream does not exist")
        return

    result = mb.get_message(name, position)

    if result:
        click.echo(result.payload)
    else:
        click.echo("No message found")

@message.command("uuid")
@click.argument("message_uuid", type=uuid.UUID)
@pass_mb
def get_message_from_uuid(mb, message_uuid):
    """Return a message with given uuid""" 

    result = mb.get_message_from_uuid(message_uuid)

    if result:
        click.echo(result.payload)
    else:
        click.echo("No message found")


@message.command("next")
@click.argument("name")
@click.argument("position", type=int)
@pass_mb
def next_message(mb, name, position):
    """Return the next message from a stream"""

    if not mb.has_stream(name):
        click.echo("The stream does not exist")
        return

    result = mb.next_message(name, position)

    if result:
        click.echo(result.stream_position)
    else:
        click.echo("At end, no more messages")

@message.command("first")
@click.argument("name")
@pass_mb
def first_message(mb, name):
    """Return the first message from a stream"""

    if not mb.has_stream(name):
        click.echo("The stream does not exist")
        return

    result = mb.first_message(name)

    if result:
        click.echo(result.stream_position)
    else:
        click.echo("No messages found")

@message.command("post")
@click.argument("name")
@click.argument("payload_filename")
@pass_mb
def post_message(mb, name, payload_filename):
    """Post a new message to a stream"""

    if not mb.has_stream(name):
        click.echo("The stream does not exist")
        return

    result = mb.post_message_from_file(name, payload_filename)

    click.echo(result)

@message.command("forward")
@click.argument("name")
@click.argument("ts", type=datetime.datetime.fromisoformat)
@click.argument("message_uuid", type=uuid.UUID)
@click.argument("payload_filename")
@pass_mb
def post_message(mb, name, ts, message_uuid, payload_filename):
    """Post an exaiting message to a stream"""

    if not mb.has_stream(name):
        click.echo("The stream does not exist")
        return

    result = mb.post_message_from_file(name, payload_filename, ts=ts, message_uuid=message_uuid)

    click.echo(result)



@message.command("del")
@click.argument("name")
@click.argument("position", type=int)
@click.argument("endposition", required=False, type=int)
@pass_mb
def del_message(mb, name, position, endposition):
    """Delete a messages from a stream""" 

    if not mb.has_stream(name):
        click.echo("The stream does not exist")
        return

    if endposition:
        mb.del_message_range(name, position, endposition)
        click.echo(f"Deleted messages from {name}:{position}-{endposition}")
    else:
        mb.del_message(name, position)
        click.echo(f"Deleted message at {name}:{position}")

@message.command("has")
@click.argument("message_uuid", type=uuid.UUID)
@pass_mb
def has_message(mb, message_uuid):
    """Check if a message with message_uuid exists""" 

    result = mb.has_message(message_uuid)

    if result:
        click.echo('True')
    else:
        click.echo('False')
        sys.exit(1) 

def main():
    """Main command starting point"""

    cli()
