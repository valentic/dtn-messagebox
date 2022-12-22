#!/usr/bin/env python

import sys

import click
import texttable as tt

import messagebox

url = 'postgresql:///messagebox'
mb = messagebox.MessageBox(url)


#- Utility functions ------------------------------------------------------

def format_ts(ts):
    if not ts:
        return '' 

    return ts.strftime('%Y-%m-%d %H:%M:%S') 

def values(result, keys):
    return [result[key] for key in keys]

        
#- Base commands ---------------------------------------------------------

@click.group()
def cli():
    pass

@cli.command()
def overview():

    results = mb.overview()

    tb = tt.Texttable()

    tb.set_deco(tb.HEADER)

    tb.header(['Stream', 'Min', 'Max', 'Count', 'Start (UTC)', 'Stop (UTC)'])
    tb.set_cols_dtype(['t', 'i', 'i', 'i', format_ts, format_ts])
    tb.set_cols_align(['l', 'r', 'r', 'r', 'c', 'c'])
    tb.set_header_align(['c', 'r', 'r', 'r', 'c', 'c'])
    tb.set_max_width(0)

    for result in results:
        tb.add_row(result.values())

    click.echo(tb.draw())


#- Stream commands --------------------------------------------------------

@cli.group()
def stream():
    pass

@stream.command('list')
def list_streams():
    
    results = mb.list_streams()

    tb = tt.Texttable()

    tb.set_deco(tb.HEADER)

    tb.header(['Stream'])
    tb.set_cols_dtype(['t'])
    tb.set_cols_align(['l'])
    tb.set_header_align(['c'])
    tb.set_max_width(0)

    for result in results:
        tb.add_row(values(result, ['name']))

    click.echo(tb.draw())

@stream.command('create')
@click.argument('name')
def create_stream(name):

    if mb.has_stream(name):
        click.echo(f'The stream already exists')
        return

    click.echo(mb.create_stream(name))

@stream.command('del')
@click.argument('name')
def del_stream(name):

    if not mb.has_stream(name):
        click.echo(f'The stream does not exist')
        return

    click.echo(mb.del_stream(name))

#- Messages commands ------------------------------------------------------

@cli.group()
def messages():
    pass

@messages.command('list')
@click.argument('name')
def list_messages(name):

    if not mb.has_stream(name):
        click.echo(f'The stream does not exist')
        return

    results = mb.list_messages(name)

    tb = tt.Texttable()

    tb.set_deco(tb.HEADER)

    tb.header(['Stream', 'Position', 'Timestamp (UTC)', 'Message ID'])
    tb.set_cols_dtype(['t', 'i', format_ts, 't'])
    tb.set_cols_align(['l', 'r', 'l', 'l'])
    tb.set_header_align(['c', 'r', 'c', 'c'])
    tb.set_max_width(0)

    for result in results:
        tb.add_row(result.values())

    click.echo(tb.draw())

@messages.command('new')
@click.argument('name')
@click.argument('ts')
def new_messages(name, ts):

    if not mb.has_stream(name): 
        click.echo(f'The stream does not exist')
        return

    results = mb.list_messages_ts(name, ts)

    tb = tt.Texttable()

    tb.set_deco(tb.HEADER)

    tb.header(['Stream', 'Position', 'Timestamp (UTC)', 'Message ID'])
    tb.set_cols_dtype(['t', 'i', format_ts, 't'])
    tb.set_cols_align(['l', 'r', 'l', 'l'])
    tb.set_header_align(['c', 'r', 'c', 'c'])
    tb.set_max_width(0)

    for result in results:
        tb.add_row(result.values())

    click.echo(tb.draw())

@messages.command('del')
@click.argument('name')
@click.argument('ts')
def del_messages(name, ts):

    result = mb.del_messages(name, ts)
    click.echo(result)

#
#- Single message commands ------------------------------------------------

@cli.group()
def message():
    pass

@message.command('get')
@click.argument('name')
@click.argument('position', type=int)
def get_message(name, position):

    if not mb.has_stream(name):
        click.echo(f'The stream does not exist')
        return

    result = mb.get_message(name, position)

    click.echo(result)

    #click.echo(result['payload']) 

@message.command('get-next')
@click.argument('name')
@click.argument('position', type=int)
def get_next_message(name, position):

    if not mb.has_stream(name):
        click.echo(f'The stream does not exist')
        return

    result = mb.get_next_message(name, position)

    click.echo(result)


@message.command('post')
@click.argument('name')
@click.argument('payload_filename')
def post_message(name, payload_filename):

    if not mb.has_stream(name):
        click.echo(f'The stream does not exist')
        return

    result = mb.post_message(name, payload_filename) 

    click.echo(result)

@message.command('del')
@click.argument('name')
@click.argument('position', type=int) 
@click.argument('endposition', required=False, type=int) 
def del_message(name, position, endposition):

    if not mb.has_stream(name):
        click.echo(f'The stream does not exist')
        return

    if endposition:
        result = mb.del_message_range(name, position, endposition)
        click.echo(f'Deleted messages from {position}-{endposition}')
    else:
        result = mb.del_message(name, position)
        click.echo(f'Deleted message at {position}')

def main():
    cli()

