#!/usr/bin/env python
"""MessageBox control program"""

import click
import texttable as tt

import messagebox

URL = "postgresql:///messagebox"
mb = messagebox.MessageBox(URL)


# Utility functions ------------------------------------------------------


def format_ts(ts):
    """Format datetime"""

    if not ts:
        return ""

    return ts.strftime("%Y-%m-%d %H:%M:%S")


def values(result, keys):
    """Return values for keys in result"""

    return [result[key] for key in keys]


# Base commands ---------------------------------------------------------


@click.group()
def cli():
    """Base command group"""


@cli.command()
def overview():
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
def list_streams():
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
def create_stream(name):
    """Create a new stream"""

    if mb.has_stream(name):
        click.echo("The stream already exists")
        return

    click.echo(mb.create_stream(name))


@stream.command("del")
@click.argument("name")
def del_stream(name):
    """Delete a stream"""

    if not mb.has_stream(name):
        click.echo("The stream does not exist")
        return

    click.echo(mb.del_stream(name))


# Messages commands ------------------------------------------------------


@cli.group()
def messages():
    "Messages command group" ""


@messages.command("list")
@click.argument("name")
def list_messages(name):
    """List messages in a stream"""

    if not mb.has_stream(name):
        click.echo("The stream does not exist")
        return

    results = mb.list_messages(name)

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


@messages.command("new")
@click.argument("name")
@click.argument("ts")
def new_messages(name, ts):
    """List new messages in a stream"""

    if not mb.has_stream(name):
        click.echo("The stream does not exist")
        return

    results = mb.list_messages_ts(name, ts)

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
def del_messages(name, ts):
    """Delete old messages"""

    result = mb.del_messages(name, ts)
    click.echo(result)


# Single message commands ------------------------------------------------


@cli.group()
def message():
    """Single message command group"""


@message.command("get")
@click.argument("name")
@click.argument("position", type=int)
def get_message(name, position):
    """Return a message at a given position in a stream"""

    if not mb.has_stream(name):
        click.echo("The stream does not exist")
        return

    result = mb.get_message(name, position)

    click.echo(result)

    # click.echo(result['payload'])


@message.command("get-next")
@click.argument("name")
@click.argument("position", type=int)
def get_next_message(name, position):
    """Return the next message from a stream"""

    if not mb.has_stream(name):
        click.echo("The stream does not exist")
        return

    result = mb.get_next_message(name, position)

    click.echo(result)


@message.command("post")
@click.argument("name")
@click.argument("payload_filename")
def post_message(name, payload_filename):
    """Post a new message to a stream"""

    if not mb.has_stream(name):
        click.echo("The stream does not exist")
        return

    result = mb.post_message(name, payload_filename)

    click.echo(result)


@message.command("del")
@click.argument("name")
@click.argument("position", type=int)
@click.argument("endposition", required=False, type=int)
def del_message(name, position, endposition):
    """Delete a message from a stream"""

    if not mb.has_stream(name):
        click.echo("The stream does not exist")
        return

    if endposition:
        mb.del_message_range(name, position, endposition)
        click.echo(f"Deleted messages from {position}-{endposition}")
    else:
        mb.del_message(name, position)
        click.echo(f"Deleted message at {position}")


def main():
    """Main command starting point"""

    cli()
