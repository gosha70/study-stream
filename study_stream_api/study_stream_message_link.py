# Copyright (c) EGOGE - All Rights Reserved.
# This software may be used and distributed according to the terms of the Apache-2.0 license.
from sqlalchemy import Column, Integer, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from .study_stream_message_link_type import StudyStreamMessageLinkType

Base = declarative_base()

class StudyStreamMessageLink(Base):
    __tablename__ = 'study_stream_message_link'

    message_id = Column(Integer, ForeignKey('study_stream_message.id', ondelete='CASCADE'), primary_key=True)
    entity_type = Column(Enum(StudyStreamMessageLinkType), primary_key=True)
    entity_id = Column(Integer, primary_key=True)

    def __init__(self, message_id, entity_type, entity_id):
        self.message_id = message_id
        self.entity_type = entity_type
        self.entity_id = entity_id

    @staticmethod
    def create(session, **kwargs):
        link = StudyStreamMessageLink(**kwargs)
        session.add(link)
        session.commit()
        return link

    @staticmethod
    def read(session, message_id, entity_type, entity_id):
        return session.query(StudyStreamMessageLink).filter_by(message_id=message_id, entity_type=entity_type, entity_id=entity_id).first()

    def update(self, session, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        session.commit()

    @staticmethod
    def delete(session, message_id, entity_type, entity_id):
        link = session.query(StudyStreamMessageLink).filter_by(message_id=message_id, entity_type=entity_type, entity_id=entity_id).first()
        if link:
            session.delete(link)
            session.commit()