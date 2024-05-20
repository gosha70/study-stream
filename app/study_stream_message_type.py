# Copyright (c) EGOGE - All Rights Reserved.
# This software may be used and distributed according to the terms of the Apache-2.0 license.
from enum import Enum
from typing import Tuple
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap, QTransform

# Static dictionary to hold additional data
icon_map = {}

class StudyStreamMessageType(Enum):
    USER = ("user_icon")
    SYSTEM = ("system_icon")
    BOOKMARK = ("file_attach_icon")

    def __init__(self, icon_key):
        self.icon_key = icon_key

    @staticmethod
    def rotate_icon(rotating_icon: QPixmap, rotate_icon_angle: int)-> Tuple[QIcon, int]:    
        rotate_icon_angle += 10
        if rotate_icon_angle > 360:
            rotate_icon_angle = 0        
        transform = QTransform().rotate(rotate_icon_angle)
        rotated_pixmap = rotating_icon.transformed(transform, mode=Qt.TransformationMode.FastTransformation)
        return QIcon(rotated_pixmap), rotate_icon_angle   
    
    def get_icon(self, app_config, asserts_path: str) -> QPixmap:
        # Debug prints
        print("Checking icon_map:", icon_map)
        print("Current key:", self)
        
        # Ensure the icon_map is a dictionary
        if not isinstance(icon_map, dict):
            raise TypeError("icon_map should be a dictionary")
    
        # Check if the icon is already cached
        if self not in icon_map:
            # Construct the icon path
            icon_path = asserts_path + app_config[self.icon_key]
            # Create the QPixmap
            pixmap = QPixmap(icon_path)
            # Cache the QPixmap
            icon_map[self] = pixmap
            return pixmap
        else:
            return icon_map[self]   
        