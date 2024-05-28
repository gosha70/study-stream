# Copyright (c) EGOGE - All Rights Reserved.
# This software may be used and distributed according to the terms of the Apache-2.0 license.
import fitz  # PyMuPDF

from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QListWidgetItem)
from PySide6.QtGui import QPixmap, QImage

from langchain_community.vectorstores import Chroma

from study_stream_api.study_stream_subject import StudyStreamSubject
from study_stream_api.study_stream_document import StudyStreamDocument
from .study_stream_object_view import StudyStreamObjectView


class StudyStreamDocumentView(QWidget):
    def __init__(
            self, 
            parent: QObject, 
            app_config, 
            main_color_scheme, 
            asserts_path: str, 
            db: Chroma, 
            load_chat_lambda,
            verbose: bool, 
            logging):
        super().__init__()
        self.parent = parent
        self.logging = logging
        self.asserts_path = asserts_path
        self.docs_db = db
        self.load_chat_lambda = load_chat_lambda
        self.color_scheme = main_color_scheme['center_panel']
        self.object_color_scheme = main_color_scheme['settings-css']
        self.app_config = app_config
        self.verbose=verbose
        self.logging = logging 
        self.doc = None
        self.pdf_files = []
        self.page_index = 0
        self.initUI()

    def get_object_view(self)-> StudyStreamObjectView:
        return self.object_view  
        
    def initUI(self):
        # Set a maximum height for the main widget
        self.setMaximumHeight(self.parent.height() - 50)

        # Central Panel: Display PDF
        central_panel = QVBoxLayout(self)

        self.pdf_view = QLabel()
        self.pdf_view.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Top Collapsible Object View Panel
        self.object_view = StudyStreamObjectView(
            parent=self.parent, 
            dependent_object=self.pdf_view,
            app_config=self.app_config, 
            color_scheme=self.object_color_scheme, 
            current_dir= self.asserts_path,
            db=self.docs_db,
            load_chat_lambda=self.load_chat_lambda,
            logging=self.logging
        ) 
        central_panel.addWidget(self.object_view, alignment=Qt.AlignmentFlag.AlignTop)  
        central_panel.addWidget(self.pdf_view)

        button_css = self.color_scheme['button-css']
        button_hover_css = self.color_scheme['button-hover-css']
        button_pressed_css = self.color_scheme['button-pressed-css']

        self.btn_prev = QPushButton('Previous Page')
        self.btn_prev.clicked.connect(self.prevPage)
        self.btn_prev.setStyleSheet(f"""
            QPushButton {{
                {button_css} 
            }}
            QPushButton:hover {{
                {button_hover_css}   
            }}
            QPushButton:pressed {{
                {button_pressed_css}
            }}
        """)
        central_panel.addWidget(self.btn_prev)


        self.btn_next = QPushButton('Next Page')
        self.btn_next.clicked.connect(self.nextPage)
        self.btn_next.setStyleSheet(f"""
            QPushButton {{
                {button_css} 
            }}
            QPushButton:hover {{
                {button_hover_css}   
            }}
            QPushButton:pressed {{
                {button_pressed_css}
            }}
        """)
        central_panel.addWidget(self.btn_next)
   
    def show_content(self, item):
        if isinstance(item, StudyStreamSubject):
            pass
        elif isinstance(item, StudyStreamDocument):  
            self.show_document(path=item.file_path)

    def openPDF(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF files (*.pdf);;All files (*)")
        self.show_document(path=path)

    def show_document(self, path: str):    
        if path:
            self.doc = fitz.open(path)
            print(f"Opened the document: {self.doc}")
            self.pdf_files.append(path)
            self.load_document()
            self.showPage(0)

    def load_document(self):
        for file in self.pdf_files:
            item = QListWidgetItem(file.split('/')[-1])
            item.setData(Qt.ItemDataRole.UserRole, file)

    def showPage(self, index):
        if self.doc:
            self.page_index = index  # Update the page_index when a new page is shown
            page = self.doc.load_page(index)  # Load the current page
            pix = page.get_pixmap()
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(img)
            self.pdf_view.setPixmap(pixmap)
            self.pdf_view.adjustSize()

    def prevPage(self):
        if self.doc and self.page_index > 0:
            self.page_index -= 1
            self.showPage(self.page_index)

    def nextPage(self):
        if self.doc and self.page_index < self.doc.page_count - 1:
            self.page_index += 1
            self.showPage(self.page_index)