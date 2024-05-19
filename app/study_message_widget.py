# Copyright (c) EGOGE - All Rights Reserved.
# This software may be used and distributed according to the terms of the Apache-2.0 license.
from PyQt5.QtWidgets import QTextBrowser, QVBoxLayout, QWidget, QTextEdit, QHBoxLayout, QLabel, QFrame, QSizePolicy
from PyQt5.QtGui import QPixmap, QFontMetrics
from PyQt5.QtCore import Qt, QDateTime
import markdown

max_height = 100 

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
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)

        # Message box as QTextBrowser
        self.message_box = QTextBrowser(self)
        self.message_box.setHtml(self.to_html(self.message))
        self.message_box.setStyleSheet(self.text_css)
        self.message_box.setFrameStyle(QFrame.NoFrame)
        self.message_box.setMaximumHeight(max_height)
        self.message_box.setOpenExternalLinks(True)
        self.message_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        #self.message_box.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        self.message_box.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Hide vertical scrollbar: ScrollBarAsNeeded

        # Adjust height dynamically
        self.adjust_message_box_height()

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

        self.main_layout.addLayout(main_layout)

    
    def adjust_message_box_height(self):      
        # Force the layout to update
        self.message_box.document().setTextWidth(self.message_box.viewport().width())
        box_size = self.message_box.document().size()
        message_len = len(self.message)
        font_metrics = QFontMetrics(self.message_box.font())
        line_height = font_metrics.height() * 2 + 20
        line_numbers = int(message_len/box_size.width()) * line_height
        text_height = max(line_numbers, max_height)
        content_height = min(text_height, box_size.height())
        self.message_box.setFixedHeight(int(content_height))  

    @staticmethod 
    def to_html(message: str) -> str:
        # Convert Markdown to HTML
        formatted_message = message.replace('\n', '<br>')
        return markdown.markdown(formatted_message)