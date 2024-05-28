# Copyright (c) EGOGE - All Rights Reserved.
# This software may be used and distributed according to the terms of the Apache-2.0 license.
from typing import List
import json
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from .study_stream_message_type import StudyStreamMessageType
from .study_stream_message import StudyStreamMessage

Base = declarative_base()

"""
Stores the information with user's notes, comments, bookamrks amd interactions  wit LLM. 
"""
class StudyStreamNote(Base):
    __tablename__ = 'study_stream_note'

    
    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('study_stream_subject.id', ondelete='CASCADE'), unique=True)
    json_content = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=False)

    subject = relationship("StudyStreamSubject", back_populates="note")

    def __init__(self, json_content: str, created_at: datetime, updated_at: datetime):
        self.json_content = json_content
        self.created_at = created_at
        self.updated_at = updated_at

    def to_messages(self) -> List[StudyStreamMessage]:
        # Check if json_content is a string and convert to list if needed
        if isinstance(self.json_content, str):
            messages_data = json.loads(self.json_content)
        else:
            messages_data = self.json_content  # assuming it's already a list
        messages = []
        for msg_data in messages_data:
            message = StudyStreamMessage(                
                type=StudyStreamMessageType(msg_data['type']),
                content=msg_data['content'],
                creation_time=datetime.fromisoformat(msg_data['created_at'])
            )
            messages.append(message)
        messages.sort(key=lambda msg: msg.created_at)
        return messages

    @staticmethod
    def messages_to_json(messages: List['StudyStreamMessage']) -> str:
        messages_dicts = [message.to_dict() for message in messages]
        return json.dumps(messages_dicts, indent=4)

    @staticmethod
    def create(session, note):
        session.add(note)
        session.commit()
        return note

    @staticmethod
    def read(session, note_id):
        return session.query(StudyStreamNote).filter_by(id=note_id).first()

    def update(self, session, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        session.commit()

    @staticmethod
    def delete(session, object_id):
        note = session.query(StudyStreamNote).filter_by(id=object_id).first()
        if note:
            session.delete(note)
            session.commit()
