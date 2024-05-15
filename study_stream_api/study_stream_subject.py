# Copyright (c) EGOGE - All Rights Reserved.
# This software may be used and distributed according to the terms of the Apache-2.0 license.
from typing import List

from .study_stream_document import StudyStreamDocument

"""
Stores the information about a class and documents associated with it.
"""
class StudyStreamSubject:
    def __init__(self, class_name: str):
        self._class_name = class_name
        self._sub_classes = []
        self._documents = []

    @property
    def class_name(self):
        return self._class_name

    @class_name.setter
    def class_name(self, value):
        self._class_name = value

    @property
    def sub_classes(self) -> List['StudyStreamClass']:
        return self._sub_classes

    @sub_classes.setter
    def sub_classes(self, value):
        self._sub_classes = value

    @property
    def documents(self) -> List[StudyStreamDocument]:
        return self._documents

    @documents.setter
    def documents(self, value):
        self._documents = value