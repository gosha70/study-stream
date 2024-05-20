# Copyright (c) EGOGE - All Rights Reserved.
# This software may be used and distributed according to the terms of the Apache-2.0 license.
from enum import Enum

class StudyStreamSchoolType(Enum):
    """
    Enum defines the status of the document in the Study Stream applicationt. 
    """
    HIGH_SCHOOL= 1
    COLLEGE = 2
    UNIVERSITY = 3
    COURSE = 4