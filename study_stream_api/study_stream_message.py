# Copyright (c) EGOGE - All Rights Reserved.
# This software may be used and distributed according to the terms of the Apache-2.0 license.
from datetime import datetime
from sqlalchemy import Column, Integer, String, TIMESTAMP, SmallInteger
from .study_stream_message_type import StudyStreamMessageType
from .study_stream_message_link import StudyStreamMessageLink, Base
from .study_stream_message_link_type import StudyStreamMessageLinkType

"""
Stores the information of user interaction and messaging with the Study Stream application. 
"""
class StudyStreamMessage(Base):
    __tablename__ = 'study_stream_message'

    id = Column(Integer, primary_key=True)
    type = Column(SmallInteger, nullable=False)
    public_content = Column(String, nullable=False)
    secret_content = Column(String)
    created_at = Column(TIMESTAMP, nullable=False)

    def __init__(self, type: StudyStreamMessageType, public_content: str, secret_content: str, created_at: datetime):
        self.type = type.value
        self.public_content = public_content
        self.secret_content = secret_content
        self.created_at = created_at.value  # Store the enum value

    @property
    def type_enum(self):
        return StudyStreamMessageType(self.type)

    # CRUD operations
    @staticmethod
    def create(session, message):
        session.add(message)
        session.commit()
        return message

    @staticmethod
    def read(session, message_id):
        return session.query(StudyStreamMessage).filter_by(id=message_id).first()

    def update(self, session, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        session.commit()

    @staticmethod
    def delete(session, message_id):
        message = session.query(StudyStreamMessage).filter_by(id=message_id).first()
        if message:
            session.delete(message)
            session.commit()

    @staticmethod
    def link_message(session, message_id, entity_type: StudyStreamMessageLinkType, entity_id):
        link = StudyStreamMessageLink(message_id=message_id, entity_type=entity_type, entity_id=entity_id)
        session.add(link)
        session.commit()
