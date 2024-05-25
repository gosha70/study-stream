# Copyright (c) EGOGE - All Rights Reserved.
# This software may be used and distributed according to the terms of the Apache-2.0 license.
import fitz  # PyMuPDF

from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QPushButton, QLabel, QFileDialog, QListWidgetItem)
from PySide6.QtGui import QPixmap, QImage

from study_stream_api.study_stream_subject import StudyStreamSubject
from study_stream_api.study_stream_document import StudyStreamDocument


class StudyStreamDocumentView(QWidget):
    def __init__(self, parent: QObject, app_config, color_scheme, asserts_path: str, verbose: bool, logging):
        super().__init__()
        self.parent = parent
        self.logging = logging
        self.asserts_path = asserts_path
        self.color_scheme = color_scheme
        self.app_config = app_config
        self.verbose=verbose
        self.logging = logging 
        self.doc = None
        self.pdf_files = []
        self.page_index = 0
        self.initUI()
        
    def initUI(self):
        # Central Panel: Display PDF
        central_panel = QVBoxLayout(self)
        self.pdf_list = QListWidget()
        self.pdf_list.clicked.connect(self.load_selected_document)
        #central_panel.addWidget(self.pdf_list)

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        central_panel.addWidget(self.label)

        button_css = self.color_scheme["button-css"]
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
        self.pdf_list.clear()
        for file in self.pdf_files:
            print(f"Loading the document from {file}")
            item = QListWidgetItem(file.split('/')[-1])
            item.setData(Qt.ItemDataRole.UserRole, file)
            self.pdf_list.addItem(item)
    
    def load_selected_document(self):
        item = self.pdf_list.currentItem()
        if item:
            path = item.data(Qt.ItemDataRole.UserRole)
            self.doc = fitz.open(path)
            self.showPage(0)        

    def showPage(self, index):
        if self.doc:
            self.page_index = index  # Update the page_index when a new page is shown
            page = self.doc.load_page(index)  # Load the current page
            pix = page.get_pixmap()
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(img)
            self.label.setPixmap(pixmap)
            self.label.adjustSize()

    def prevPage(self):
        if self.doc and self.page_index > 0:
            self.page_index -= 1
            self.showPage(self.page_index)

    def nextPage(self):
        if self.doc and self.page_index < self.doc.page_count - 1:
            self.page_index += 1
            self.showPage(self.page_index)