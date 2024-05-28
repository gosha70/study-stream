# Copyright (c) EGOGE - All Rights Reserved.
# This software may be used and distributed according to the terms of the Apache-2.0 license.
from datetime import datetime
import pytz
from .study_stream_message_type import StudyStreamMessageType

"""
Stores the information of user interaction and messaging with the Study Stream application. 
"""
class StudyStreamMessage:

    def __init__(self, type: StudyStreamMessageType, content: str):
        self.type = type
        self.content = content
        self.created_at = datetime.now(tz=pytz.utc)

    def to_dict(self):
        return {
            'type': self.type.value,
            'content': self.content,
            'created_at': self.created_at.isoformat()
        }