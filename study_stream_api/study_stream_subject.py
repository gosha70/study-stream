# Copyright (c) EGOGE - All Rights Reserved.
# This software may be used and distributed according to the terms of the Apache-2.0 license.
from typing import List
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from .study_stream_document import StudyStreamDocument
from .study_stream_note import StudyStreamNote
from .study_stream_note import Base

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
    note = relationship("StudyStreamNote", uselist=False, back_populates="subject", cascade="all, delete-orphan", primaryjoin="StudyStreamSubject.id == StudyStreamNote.subject_id")

    def __init__(self, class_name: str):
        self.class_name = class_name

    def add_document(self, document: StudyStreamDocument):
        self.documents.append(document)

    # CRUD operations
    @staticmethod
    def create(session, subject):
        session.add(subject)
        session.commit()
        return subject
    
    def update_note(self, session, json_content: str):
        if not self.note:
            print(f"StudyStreamNote - new")
            self.note = StudyStreamNote(json_content=json_content, created_at=datetime.now(), updated_at=datetime.now())
            self.note.subject_id = self.id
            session.add(self.note)
        else:
            print(f"StudyStreamNote - update")
            self.note.json_content = json_content
            self.note.updated_at = datetime.now()
        session.commit()

    @staticmethod
    def read(session, subject_id)-> 'StudyStreamSubject':
        return session.query(StudyStreamSubject).filter_by(id=subject_id).first()

    def update(self, session, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        session.commit()

    @staticmethod
    def delete(session, object_id):
        subject = session.query(StudyStreamSubject).filter_by(id=object_id).first()
        if subject:
            session.delete(subject)
            session.commit()
