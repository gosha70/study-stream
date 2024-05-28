# Copyright (c) EGOGE - All Rights Reserved.
# This software may be used and distributed according to the terms of the Apache-2.0 license.
from datetime import datetime
from typing import List
import pytz

from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, SmallInteger
from sqlalchemy.orm import relationship

from .study_stream_message import StudyStreamMessage
from .study_stream_note import Base
from .study_stream_document_status import StudyStreamDocumentStatus

from embeddings.unstructured.file_type import FileType

"""
Stores the information about a class document a student added and read 
in the Study Stream application. 
"""
class StudyStreamDocument(Base):
    __tablename__ = 'study_stream_document'

    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('study_stream_subject.id', ondelete='CASCADE'))
    name = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    file_type = Column(SmallInteger, nullable=False)
    status = Column(SmallInteger, nullable=False)
    creation_date = Column(TIMESTAMP, nullable=False, default=datetime.now)
    in_progress_date = Column(TIMESTAMP)
    processed_date = Column(TIMESTAMP)

    def __init__(self, name: str, file_path: str, file_type_enum: FileType, status_enum: StudyStreamDocumentStatus):
        self.name = name
        self.file_path = file_path
        self.file_type = file_type_enum.int_value  # Store the enum value
        self.status = status_enum.value  # Store the enum value
        self.creation_date = datetime.now(tz=pytz.utc)
        self.in_progress_date = None
        self.processed_date = None
     
    @property
    def status_enum(self):
        return StudyStreamDocumentStatus(self.status)

    @status_enum.setter
    def status_enum(self, value: StudyStreamDocumentStatus):
        self.status = value.value
        if self.status == StudyStreamDocumentStatus.IN_PROGRESS:
            self.in_progress_date = datetime.now()
        elif self.status == StudyStreamDocumentStatus.PROCESSED:   
            self.processed_date = datetime.now() 
    
    @property
    def file_type_enum(self):
        return FileType.from_int(self.file_type)

    @file_type_enum.setter
    def file_type_enum(self, value: FileType):
        self.file_type = value.int_value  
    
    def add_message(self, session, message: StudyStreamMessage):
        StudyStreamMessage.link_message(session, message.id, StudyStreamNoteLinkType.DOCUMENT, self.id)

    # CRUD operations
    @staticmethod
    def create(session, document):
        session.add(document)
        session.commit()
        return document

    @staticmethod
    def read(session, document_id):
        return session.query(StudyStreamDocument).filter_by(id=document_id).first()

    def update(self, session, **update_values):
        for key, value in update_values.items():
            setattr(self, key, value)
        session.commit()

    @staticmethod
    def delete(session, object_id):
        document = session.query(StudyStreamDocument).filter_by(id=object_id).first()
        if document:
            session.delete(document)
            session.commit()
