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
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv(".env")

debug = os.environ.get("MESSAGEBOX_DEBUG", "0").lower() in ["1", "true"]

url = os.environ.get("MESSAGEBOX_URL", "postgresql:///messagebox")
engine = create_engine(url, echo=debug)
Session = sessionmaker(engine)

