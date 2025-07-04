#!/usr/bin/env python3
"""Database Models."""

###########################################################################
#
#   MessageBox Data Models
#
#   Needs postgresql postgresql-server sqlalchemy
#
#   2024-01-05  Todd Valentic
#               Initial implementation.
#
#   2025-07-01  Todd Valentic
#               Convert to MessageLane (lane -> lane)
#
###########################################################################

import datetime
import uuid

from sqlalchemy import ForeignKey, BigInteger, DateTime, Uuid
from sqlalchemy import Index, func, FetchedValue, text, MetaData

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import DeclarativeBase

from .db import engine

# --------------------------------------------------------------------------
#   Helper functions and types
# --------------------------------------------------------------------------


def create_all():
    """Create all tables."""
    Model.metadata.create_all(engine)


def drop_all():
    """Drop all tables."""
    Model.metadata.drop_all(engine)


class Model(DeclarativeBase):
    """Base class for data models."""

    metadata = MetaData(
        naming_convention=(
            {
                "ix": "ix_%(column_0_label)s",
                "uq": "uq_%(table_name)s_%(column_0_name)s",
                "ck": "ck_%(table_name)s_%(constraint_name)s",
                "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
                "pk": "pk_%(table_name)s",
            }
        )
    )


# --------------------------------------------------------------------------
#   Tables
# --------------------------------------------------------------------------


class Message(Model):
    """Message table."""

    __tablename__ = "message"
    __table_args__ = (Index("ix_message_lane_id_ts", "lane_id", "ts"),)

    message_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    message_uuid: Mapped[uuid.UUID] = mapped_column(
        Uuid, server_default=text("gen_random_uuid()"), unique=True, index=True
    )
    lane_id: Mapped[int] = mapped_column(ForeignKey("lane.lane_id"), index=True)

    lane_position: Mapped[int] = mapped_column(
        BigInteger, server_default=FetchedValue()
    )
    ts: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    payload: Mapped[str]
    payload_hash: Mapped[bytes] = mapped_column(index=True)
    payload_size: Mapped[int]

    lane: Mapped["Lane"] = relationship(back_populates="messages")

    def __repr__(self):
        """Return a string representation of the message."""
        return (
            f"Message({self.message_id}, {self.ts}, "
            f"{self.message_uuid}, {self.lane_position})"
        )


class Lane(Model):
    """Lane table."""

    __tablename__ = "lane"

    lane_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(index=True, unique=True)
    marker: Mapped[int] = mapped_column(BigInteger, insert_default=0)

    messages: Mapped[list["Message"]] = relationship(
        cascade="all, delete-orphan", back_populates="lane"
    )

    def __repr__(self):
        """Return a string representation of the lane."""
        return f"Lane({self.lane_id}, {self.name}, {self.marker})"
