#!/usr/bin/env python3
"""Database Interaction"""

###########################################################################
#
#   Database Interaction 
#
#   Needs postgresql postgresql-server sqlalchemy (2.x)
#
#   2024-01-05  Todd Valentic
#               Initial implementation.
#
###########################################################################

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker 

class Model(DeclarativeBase):

    metadata = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    })

load_dotenv(".env")

echo = os.environ.get("MESSAGEBOX_ECHO", "0").lower() in ["1", "true"]

#url = os.environ.get("MESSAGEBOX_URL", "postgresql:///messagebox")
url = os.environ.get("MESSAGEBOX_URL", "postgresql:///messagebox2")
engine = create_engine(url, echo=echo)
Session = sessionmaker(engine)

