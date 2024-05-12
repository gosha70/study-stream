import sys
import os
import fitz  # PyMuPDF
import json
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QFileDialog, QListWidget, QListWidgetItem,
                             QTextEdit)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

from .curriculum_panel import CurriculumPanel

class PDFViewer(QWidget):
    def __init__(self):
        super().__init__()
        # Set the working directory to the script's directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        self.current_dir = os.getcwd()
        with open(self.current_dir + '/app_config.json', 'r') as file:
            self.app_config = json.load(file)  
        with open(self.current_dir + '/color_schemes/dark-color-scheme.json', 'r') as file:
            self.color_scheme = json.load(file)  
        self.initUI()
        self.doc = None
        self.pdf_files = []
        self.page_index = 0  # Initialize page_index here

    def initUI(self):
        # Main layout
        main_layout = QHBoxLayout(self)

        # Left Panel: Toolbar and List of PDFs
        left_panel = CurriculumPanel(
            parent=self, 
            app_config=self.app_config, 
            color_scheme=self.color_scheme["left_panel"],
            asserts_path=self.current_dir
        )

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

        # Right Panel: Chat with LLM
        right_panel = QVBoxLayout()
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        right_panel.addWidget(self.chat_display)

        self.chat_input = QTextEdit()
        self.chat_input.setFixedHeight(100)
        right_panel.addWidget(self.chat_input)

        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.sendMessage)
        right_panel.addWidget(self.send_button)

        # Add all panels to the main layout
        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(central_panel, 3)  # Central panel takes 70% space
        main_layout.addLayout(right_panel, 1)

        self.setGeometry(300, 300, 1200, 800)
        self.setWindowTitle('PDF and LLM Viewer')
        self.show()

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

    def sendMessage(self):
        user_text = self.chat_input.toPlainText()
        self.chat_display.append("You: " + user_text)
        # Placeholder for LLM response
        self.chat_display.append("LLM: " + "Thank you for your message. How can I assist you further?")
        self.chat_input.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PDFViewer()
    sys.exit(app.exec_())
