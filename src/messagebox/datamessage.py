#!/usr/bin/env python
"""Data Messsage."""

##########################################################################
#
#   DataMessage
#
#   Create email format data messages
#
#   2023-01-07  Todd Valentic
#               Initial implementation
#
##########################################################################

import mimetypes

from email.message import EmailMessage
from email.policy import SMTP
from pathlib import Path


class DataMessage:
    """Data Transport Message."""

    def __init__(self, **kw):
        """Initialize DataMessage instance."""
        self.headers = {
            "From": "transport@local",
            "To": "transport@local",
            "Subject": "Data Transport Message",
        }

        self.set(**kw)

    def set(self, **kw):
        """Set cached headers."""
        self.headers.update(kw)

    def __call__(self, filenames=None, comment=None, date=None, headers=None):
        """Generate an email formatted message."""
        if filenames is None:
            filenames = []

        msg = EmailMessage(policy=SMTP)
        msg.preamble = comment

        for key, value in self.headers.items():
            msg[key] = value

        if date:
            msg["X-Transport-Date"] = str(date)

        if headers:
            for key, value in headers.items():
                msg[key] = value

        for filename in filenames:
            path = Path(filename)

            if not path.exists():
                continue

            ctype, encoding = mimetypes.guess_type(path)

            if ctype is None or encoding is not None:
                ctype = "application/octet-stream"

            maintype, subtype = ctype.split("/", 1)

            with open(path, "rb") as fp:
                msg.add_attachment(
                    fp.read(), maintype=maintype, subtype=subtype, filename=path.name
                )

        return msg
