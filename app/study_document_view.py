# Copyright (c) EGOGE - All Rights Reserved.
# This software may be used and distributed according to the terms of the Apache-2.0 license.
import fitz  # PyMuPDF

from PyQt5.QtCore import QObject, Qt
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QListWidgetItem)
from PyQt5.QtGui import QPixmap, QImage


class StudyDocumentView(QWidget):
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
        central_panel = QVBoxLayout()
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        central_panel.addWidget(self.label)

        self.btn_prev = QPushButton('Previous Page')
        self.btn_prev.clicked.connect(self.prevPage)
        central_panel.addWidget(self.btn_prev)

        self.btn_next = QPushButton('Next Page')
        self.btn_next.clicked.connect(self.nextPage)
        central_panel.addWidget(self.btn_next)

    def openPDF(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF files (*.pdf);;All files (*)")
        if path:
            self.doc = fitz.open(path)
            self.pdf_files.append(path)
            self.updatePDFList()
            self.showPage(0)

    def updatePDFList(self):
        self.pdf_list.clear()
        for file in self.pdf_files:
            item = QListWidgetItem(file.split('/')[-1])
            self.pdf_list.addItem(item)

    def showPage(self, index):
        if self.doc:
            self.page_index = index  # Update the page_index when a new page is shown
            page = self.doc.load_page(index)  # Load the current page
            pix = page.get_pixmap()
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
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