# Copyright (c) EGOGE - All Rights Reserved.
# This software may be used and distributed according to the terms of the Apache-2.0 license.
from typing import List

from .study_stream_subject import StudyStreamSubject

"""
Stores the information about a class and documents associated with it.
"""
class StudyStreamInstitution:
    def __init__(self, class_name: str):
        self._name = class_name
        self._classes = []

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def classes(self) -> List[StudyStreamSubject]:
        return self._classes

    @classes.setter
    def classes(self, value):
        self._classes = value