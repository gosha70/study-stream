# Copyright (c) EGOGE - All Rights Reserved.
# This software may be used and distributed according to the terms of the Apache-2.0 license.
from typing import List
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from .study_stream_document import StudyStreamDocument
from .study_stream_message import StudyStreamMessage
from .study_stream_message_link import Base
from .study_stream_message_link_type import StudyStreamMessageLinkType

"""
Stores the information about a class and documents associated with it.
"""
class StudyStreamSubject(Base):
    __tablename__ = 'study_stream_subject'

    id = Column(Integer, primary_key=True)
    school_id = Column(Integer, ForeignKey('study_stream_school.id', ondelete='CASCADE'))
    class_name = Column(String(255), nullable=False)
    start_date = Column(TIMESTAMP, nullable=False, default=datetime.now)
    finish_date = Column(TIMESTAMP)

    documents = relationship('StudyStreamDocument', backref='subject', cascade='all, delete-orphan')

    def __init__(self, class_name: str):
        self.class_name = class_name

    @property
    def messages(self) -> List[StudyStreamMessage]:
        return self.messages
    
    def add_message(self, session, message: StudyStreamMessage):
        StudyStreamMessage.link_message(session, message.id, StudyStreamMessageLinkType.SUBJECT, self.id)

    def add_document(self, document: StudyStreamDocument):
        self.documents.append(document)

    # CRUD operations
    @staticmethod
    def create(session, subject):
        session.add(subject)
        session.commit()
        return subject

    @staticmethod
    def read(session, subject_id):
        return session.query(StudyStreamSubject).filter_by(id=subject_id).first()

    def update(self, session, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        session.commit()

    @staticmethod
    def delete(session, subject_id):
        subject = session.query(StudyStreamSubject).filter_by(id=subject_id).first()
        if subject:
            session.delete(subject)
            session.commit()
