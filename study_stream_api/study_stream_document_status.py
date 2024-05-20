# Copyright (c) EGOGE - All Rights Reserved.
# This software may be used and distributed according to the terms of the Apache-2.0 license.
from enum import Enum

class  StudyStreamDocumentStatus(Enum):
    """
    Enum defines the status of the document in the Study Stream applicationt. 
    """
    NEW = 1
    IN_PROGRESS = 2
    PROCESSED = 3
    