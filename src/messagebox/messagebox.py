#!/usr/bin/env python
"""MessageBox"""

##########################################################################
#
#   MessageBox Interface
#
#   Python library for interfacing with the MessageBox database.
#
#   2022-12-21  Todd Valentic
#               Initial implementation
#
##########################################################################

import sys
import datetime

import pugsql

if sys.version_info < (3, 10):
    import importlib_resources as resources
else:
    from importlib import resources


class MessageBox:
    """MessageBox API"""

    def __init__(self, url):

        src = resources.files("messagebox.sql.api")

        with resources.as_file(src) as api:
            self.db = pugsql.module(api)

        self.db.connect(url)

    def has_stream(self, name):
        """Test if stream exists"""
        return self.db.get_stream(name=name) is not None

    def get_stream(self, name):
        """Return stream entry"""

        return self.db.get_stream(name=name)

    def overview(self):
        """Return messagebox summary overview"""

        return self.db.overview()

    # Stream commands ----------------------------------------------------

    def list_streams(self):
        """List streams"""

        return self.db.list_streams()

    def create_stream(self, name):
        """Create a new stream"""

        with self.db.transaction() as _t:
            return self.db.create_stream(name=name)

    def del_stream(self, name):
        """Delet a stream"""

        with self.db.transaction() as _t:
            return self.db.del_stream(name=name)

    # Messages commands --------------------------------------------------

    def list_messages(self, name):
        """List messages in a stream"""

        return self.db.list_messages(name=name)

    def list_messages_ts(self, name, ts):
        """List new messages since ts"""

        return self.db.list_messages_ts(name=name, ts=ts)

    def del_messages(self, name_pattern, ts):
        """Delete messages from streams since ts"""

        with self.db.transaction() as _t:
            return self.db.del_messages(name_pattern=name_pattern, ts=ts)

    # Single message commands --------------------------------------------

    def get_message(self, name, position):
        """Return a message from a stream"""

        return self.db.get_message(name=name, position=position)

    def get_next_message(self, name, position):
        """Return the next message from a stream"""

        return self.db.get_next_message(name=name, position=position)

    def post_message(self, name, payload_filename):
        """Post a new message from a file to a stream"""

        ts = datetime.datetime.now(datetime.timezone.utc)

        with open(payload_filename, "r", encoding="utf8") as payload:
            contents = payload.read()

        with self.db.transaction() as _t:
            return self.db.post_message(name=name, ts=ts, payload=contents)

    def del_message(self, name, position):
        """Delete a message from a stream at a given position"""

        with self.db.transaction() as _t:
            return self.db.del_message(name=name, position=position)

    def del_message_range(self, name, start_pos, stop_pos):
        """Delete a message from a stream between positions"""

        with self.db.transaction() as _t:
            return self.db.del_message_range(name=name, start=start_pos, stop=stop_pos)
