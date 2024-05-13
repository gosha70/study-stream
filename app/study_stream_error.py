# Copyright (c) EGOGE - All Rights Reserved.
# This software may be used and distributed according to the terms of the Apache-2.0 license.

class StudyStreamException(Exception):
    """Exception raised in Study Stream Application."""
    def __init__(self, message):
        self.message = message
        super().__init__(f"{message}: {value}")