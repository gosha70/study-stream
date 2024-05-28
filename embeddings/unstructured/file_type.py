# Copyright (c) EGOGE - All Rights Reserved.
# This software may be used and distributed according to the terms of the CC-BY-SA-4.0 license.
from enum import Enum

class FileType(Enum):
    """
    Enum defines supported file types/extensions
    """
    CSV = (1, "csv")
    DDL = (2, "ddl")
    EXCEL = (3, "xlsx")
    JAVA = (4, "java")
    JS = (5, "js")
    JSON = (6, "json")
    HTML = (7, "html")
    MARKDOWN = (8, "md")
    PDF = (9, "pdf")
    PYTHON = (10, "py")
    RICH_TEXT = (11, "rtf")
    SQL = (12, "sql")
    TEXT = (13, "txt")
    XML = (14, "xml")
    XSL = (15, "xsl")
    YAML = (16, "yaml")

    @property
    def int_value(self) -> int:
        return self.value[0]

    @property
    def str_value(self) -> str:
        return self.value[1]

    @classmethod
    def from_int(cls, int_value):
        for member in cls:
            if member.int_value == int_value:
                return member
        raise ValueError(f"No matching enum for int value {int_value}")

    @classmethod
    def from_str(cls, str_value):
        for member in cls:
            if member.str_value == str_value:
                return member
        raise ValueError(f"No matching enum for str value {str_value}")

    def get_extension(self) -> str:
        return f".{self.str_value}"
    
    @staticmethod    
    def from_str_by_extension(file_name: str):
        """Returns the FileType for a given file name."""
        # Extract the extension from the file name
        extension = file_name.split('.')[-1]
        # Iterate through the FileType enum to find a match
        for file_type in FileType:
            if file_type.str_value == extension:
                return file_type
        return None
