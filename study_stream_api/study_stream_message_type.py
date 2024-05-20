# Copyright (c) EGOGE - All Rights Reserved.
# This software may be used and distributed according to the terms of the Apache-2.0 license.
from enum import Enum

class StudyStreamMessageType(Enum):
    QUESTION = 1
    ANSWER = 2
    BOOKMARK = 3
    COMMENT = 4
    SENTIMENT = 5