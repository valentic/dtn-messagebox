"""A MessageBox client class.

...

Example:
-------
>>> from messagebox import db, MessageBox
>>> session = db.Session()
>>> mb = MessageBox(session)
>>> mb.overview()

"""

##########################################################################
#
#   MessageBox Interface
#
#   Python library for interfacing with the MessageBox database.
#
#   2022-12-21  Todd Valentic
#               Initial implementation
#
#   2024-01-05  Todd Valentic
#               Use sqlalchemy instead of pugsql
#
##########################################################################

import hashlib
import sqlalchemy as sa

from .models import Stream, Message


class MessageBox:
    """The MessageBox API."""

    def __init__(self, session):
        """Initialize MessageBox instance."""
        self.session = session

    def has_stream(self, name):
        """Test if stream exists."""
        return self.get_stream(name) is not None

    def get_stream(self, name):
        """Return stream entry matching name."""
        stmt = sa.select(Stream).where(Stream.name == name)
        return self.session.scalar(stmt)

    def overview(self):
        """Return messagebox summary overview."""
        messages = sa.select(Message).lateral()

        stmt = (
            sa.select(
                Stream.name,
                sa.func.coalesce(sa.func.min(messages.c.stream_position), 0).label(
                    "min_position"
                ),
                sa.func.coalesce(sa.func.max(messages.c.stream_position), 0).label(
                    "max_position"
                ),
                sa.func.count(messages.c.stream_position).label("count"),
                sa.func.min(messages.c.ts).label("min_ts"),
                sa.func.max(messages.c.ts).label("max_ts"),
                sa.func.sum(messages.c.payload_size).label("size")
            )
            .outerjoin(messages)
            .group_by(Stream.stream_id)
            .order_by(Stream.name)
        )

        return [row._mapping for row in self.session.execute(stmt)]

    def status(self):
        """Return messagebox database status."""

        engine = self.session.bind
        dbname = engine.url.database

        dbsize_sql = sa.text("SELECT pg_database_size(:name)")

        dbsize = self.session.scalar(dbsize_sql, {"name": dbname})

        table_size_sql = sa.text("SELECT pg_total_relation_size(:name)")

        tables = ["stream", "message"]

        table_results = {}

        for name in tables:
            # We can only pass values as parameters, not table names.
            # So dynamically create sql here
            table_rows_sql = sa.text(f"SELECT count(*) from {name}")

            size = self.session.scalar(table_size_sql, {"name": name})
            rows = self.session.scalar(table_rows_sql)
            table_results[name] = { "size": size, "rows": rows } 

        indexes_sql = sa.text(
                        "select tablename, indexname from pg_indexes "
                        "where schemaname = 'public' "
                        "order by tablename, indexname"
                    )

        indexes = self.session.execute(indexes_sql).all()

        index_sizes = {}

        for tablename, indexname in indexes:
            if not tablename in index_sizes:
                index_sizes[tablename] = {}
            size = self.session.scalar(table_size_sql, {"name": indexname})
            index_sizes[tablename][indexname] = size

        return {
            "database": {
                "name": dbname,
                "size": dbsize
            },
            "table": table_results,
            "index": index_sizes,
        }

    # Stream commands ----------------------------------------------------

    def list_streams(self):
        """List streams."""
        return self.session.scalars(sa.select(Stream))

    def create_stream(self, name):
        """Create a new stream."""
        stream = Stream(name=name)
        self.session.add(stream)

    def del_stream(self, name):
        """Delete a stream."""
        stmt = sa.select(Stream).where(Stream.name == name)
        stream = self.session.scalar(stmt)

        self.session.delete(stream)

        return stream

    # Messages commands --------------------------------------------------

    def list_messages(self, name):
        """List messages in a stream."""
        stmt = (
            sa.select(Message)
            .join(Message.stream)
            .where(Stream.name == name)
            .order_by(Message.stream_position)
        )

        return self.session.scalars(stmt)

    def list_messages_ts(self, name, ts):
        """List new messages since ts."""
        stmt = (
            sa.select(
                Stream.name, Message.stream_position, Message.ts, Message.message_uuid
            )
            .join(Message.stream)
            .where(Stream.name == name)
            .where(Message.ts >= ts)
            .order_by(Message.stream_position)
        )

        return self.session.scalars(stmt)

    def del_messages(self, name_pattern, ts):
        """Delete messages from streams since ts."""
        stream_ids = sa.select(Stream.stream_id).where(Stream.name.like(name_pattern))

        stmt = (
            sa.delete(Message)
            .where(Message.stream_id.in_(stream_ids))
            .where(Message.ts <= ts)
        )

        return self.session.execute(stmt)

    # Single message commands --------------------------------------------

    def get_message(self, name, position):
        """Return a message from a stream."""
        stream = self.get_stream(name)
        stmt = (
            sa.select(Message)
            .where(Message.stream_position == position)
            .where(Message.stream == stream)
        )

        return self.session.scalar(stmt)

    def first_message(self, name):
        """Return the first message from a stream."""
        stream = self.get_stream(name)
        stmt = (
            sa.select(Message)
            .where(Message.stream == stream)
            .order_by(Message.stream_position)
            .limit(1)
        )

        return self.session.scalar(stmt)

    def next_message(self, name, position):
        """Return the next message from a stream."""
        stream = self.get_stream(name)
        stmt = (
            sa.select(Message)
            .where(Message.stream == stream)
            .where(Message.stream_position > position)
            .limit(1)
        )

        return self.session.scalar(stmt)

    def post_message_from_email(self, name, email, **kw):
        """Post a new message from a file to a stream."""
        return self.post_message(name, email.as_string(), **kw)

    def post_message_from_file(self, name, filename, **kw):
        """Post a new message from a file to a stream."""
        with open(filename, "r", encoding="utf8") as f:
            payload = f.read()

        return self.post_message(name, payload, **kw)

    def post_message(self, name, payload, ts=None, message_uuid=None):
        """Post a message to a stream."""
        payload_hash = hashlib.md5(payload.encode()).digest()

        return_args = [
            Stream.stream_id,
            Stream.marker,
            sa.cast(payload, sa.String).label("payload"),
            sa.cast(payload_hash, sa.LargeBinary).label("hash"),
            sa.cast(len(payload), sa.Integer).label("payload_size")
        ]

        cols = [
            "stream_id", 
            "stream_position", 
            "payload", 
            "payload_hash", 
            "payload_size"
        ]

        if ts:
            return_args.append(sa.cast(ts, sa.TIMESTAMP(timezone=True)).label("ts"))
            cols.append("ts")

        if message_uuid:
            return_args.append(sa.cast(message_uuid, sa.Uuid).label("message_uuid"))
            cols.append("message_uuid")

        cte = (
            sa.update(Stream)
            .where(Stream.name == name)
            .values(marker=Stream.marker + 1)
            .returning(*return_args)
            .cte()
        )

        stmt = sa.insert(Message).from_select(cols, cte).returning(Message.message_uuid)

        return self.session.scalar(stmt)

    def del_message(self, name, position):
        """Delete a message from a stream at a given position."""
        stream = self.get_stream(name)

        stmt = (
            sa.delete(Message)
            .where(Message.stream == stream)
            .where(Message.stream_position == position)
        )

        self.session.execute(stmt)

    def del_message_range(self, name, first_position, last_position):
        """Delete a message from a stream between positions."""
        stream = self.get_stream(name)

        stmt = (
            sa.delete(Message)
            .where(Message.stream == stream)
            .where(Message.stream_position >= first_position)
            .where(Message.stream_position <= last_position)
        )

        self.session.execute(stmt)

    def get_message_from_uuid(self, message_uuid):
        """Return message with matching uuid."""
        stmt = sa.select(Message).where(Message.message_uuid == message_uuid)

        return self.session.scalar(stmt)

    def has_message_uuid(self, message_uuid):
        """Check if message with uuid is in database."""
        return self.get_message_from_uuid(message_uuid) is not None

    def get_message_from_hash(self, ts, payload_hash):
        """Return message with matching timestamp and payload hash."""
        stmt = (
            sa.select(Message)
            .where(Message.payload_hash == payload_hash)
            .where(Message.ts == ts)
        )

        return self.session.scalar(stmt)

    def has_message_hash(self, ts, payload_hash):
        """Check if message with timestamp and hash is in database."""
        return self.get_message_from_hash(ts, payload_hash) is not None

