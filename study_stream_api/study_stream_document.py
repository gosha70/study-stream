# Copyright (c) EGOGE - All Rights Reserved.
# This software may be used and distributed according to the terms of the Apache-2.0 license.
from enum import Enum
from datetime import datetime

from embeddings.unstructured.file_type import FileType

class DocumentStatus(Enum):
    """
    Enum defines the status of the document in the Study Stream applicationt. 
    """
    NEW = 1
    IN_PROGRESS = 2
    PROCESSED = 3
    

"""
Stores the information about a class document a student added  and read 
in the Study Stream applicationt. 
"""
class StudyStreamDocument:
    def __init__(
            self, 
            name: str, 
            file_path: str, 
            file_type: FileType, 
            status: DocumentStatus):
        self._name = name
        self._file_path = file_path
        self._file_type = file_type
        self._status = status
        ## LATER - allow to specify the creation date
        self._creation_date = datetime.now()
        self._in_progress_date = None
        self._processed_date = None
    
    @property
    def creation_date(self):
        return self._creation_date
    
    @property
    def in_progress_date(self):
        return self._in_progress_date
    
    @property
    def processed_date(self):
        return self._processed_date
    
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
    
    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, value):
        self._file_path = value
    
    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value
        if self._status == DocumentStatus.IN_PROGRESS:
            self._in_progress_date = datetime.now()
        elif self._status == DocumentStatus.PROCESSED:   
            self._processed_date = datetime.now() 
    
    @property
    def file_type(self):
        return self._file_type

    @file_type.setter
    def file_type(self, value):
        self._file_type = value    
    
    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value    

    