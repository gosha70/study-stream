import os
from pathlib import Path
from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QMenu
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings
from urllib.parse import quote

# Set the environment variable for the dictionaries
os.environ['QTWEBENGINE_DICTIONARIES_PATH'] = '/path/to/your/dictionaries'

class PDFView(QWidget):
    
    textSelected = Signal(str)

    def __init__(self, parent=None, ai_observer=None):
        super().__init__(parent)
        self.ai_observer = ai_observer
        script_directory = Path(__file__).resolve().parent
        self.pdf_js_path = script_directory / "PDF_js" / "web" / "viewer.html"
        print('PDF.js viewer path:', self.pdf_js_path)
        self.pdf_path = ""
        self.current_page = 1

        self.web_view = QWebEngineView()

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.web_view)

        self.settings = self.web_view.settings()
        self.settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.settings.setAttribute(QWebEngineSettings.PdfViewerEnabled, True)
        self.settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, True)

        self.web_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.web_view.customContextMenuRequested.connect(self.show_context_menu)

        self.context_menu = QMenu(self)
        self.send_chat_action = self.context_menu.addAction("Send to Chat")
        self.send_chat_action.triggered.connect(self.send_to_chat)

    def show_context_menu(self, pos):
        selected_text = self.web_view.page().selectedText()
        if selected_text:
            self.context_menu.exec(self.web_view.mapToGlobal(pos))

    def send_to_chat(self):
        reference_text = "Please examplain this to me ?\n====\n" + self.web_view.page().selectedText() + "\n==="
        print('Text to be sent to chat:', reference_text)
        if self.ai_observer:
            if self.ai_observer(reference_text):
                print('The text was sent')
            else: 
                print('Cannot send the text! The chat is busy!')     

    def show_pdf(self, file_path):
        # Encode the file path to handle spaces and special characters
        encoded_file_path = quote(file_path)
        full_url = QUrl(f'file:///{self.pdf_js_path}?file=file:///{encoded_file_path}#page={self.current_page}')
        print('this is full url:', full_url.toString())
        self.web_view.load(full_url)
