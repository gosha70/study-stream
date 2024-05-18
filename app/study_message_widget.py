# Copyright (c) EGOGE - All Rights Reserved.
# This software may be used and distributed according to the terms of the Apache-2.0 license.
from PyQt5.QtCore import Qt, QDateTime, QSize
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QTextEdit, QSizePolicy, QHBoxLayout, QLabel, QFrame
from PyQt5.QtGui import QPixmap


class StudyMessageWidget(QWidget):
    def __init__(self, message, icon: QPixmap, text_css: str, icon_css: str, datetime_css: str):
        super().__init__()
        self.message = message
        self.icon = icon
        self.text_css = text_css
        self.icon_css = icon_css
        self.datetime_css = datetime_css
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(0)

        # Message box
        self.message_box = QTextEdit(self)
        self.message_box.setReadOnly(True)
        self.message_box.setText(self.message)
        self.message_box.setFrameStyle(QFrame.NoFrame)
        self.message_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.message_box.setStyleSheet(self.text_css)
        
        # Icon
        icon_label = QLabel(self)
        icon_label.setPixmap(self.icon.scaled(32, 32, Qt.KeepAspectRatio))
        icon_label.setStyleSheet(self.icon_css)

        # Timestamp
        timestamp_label = QLabel(QDateTime.currentDateTime().toString(), self)
        timestamp_label.setAlignment(Qt.AlignRight)
        timestamp_label.setStyleSheet(self.datetime_css)

        # Top level horizontal layout
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(10)
        top_layout.addWidget(icon_label)
        top_layout.addStretch()
        top_layout.addWidget(timestamp_label)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.message_box)

        self.layout.addLayout(main_layout)
