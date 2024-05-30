import os
from pathlib import Path
from PySide6.QtCore import Qt, QUrl, Signal, QObject, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QMenu, QInputDialog
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtGui import QIcon
from urllib.parse import quote

# Set the environment variable for the dictionaries
#os.environ['QTWEBENGINE_DICTIONARIES_PATH'] = '/path/to/your/dictionaries'

class Bridge(QObject):
    pageNumber = Signal(str)

    @Slot(str)
    def cuePageNum(self, number):
        print('bridge num', number)
        self.pageNumber.emit(number)

class StudyStreamPdfView(QWidget):
    
    textSelected = Signal(str)
    bookmark_signal = Signal(dict)

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
        self.context_menu.setStyleSheet("""            
            QMenu {
                height: 150px;   
                background-color: white;
            }                            
            QMenu::item {
                margin: 0px;
                height: 50px;   
                min-height: 24px;    
            }
            QMenu::item:selected {
                background-color: #d3d3d3;
            }
            QMenu::separator {
                height: 2px;
                background: #d3d3d3;
                margin: 2px 0;
            }
        """)
        self.send_chat_action = self.context_menu.addAction("Explain Selected Text")
        self.bookmark_action = self.context_menu.addAction("Create Bookmark")
        self.send_chat_action.triggered.connect(self.send_to_chat)
        self.bookmark_action.triggered.connect(self.add_bookmark)

        self.channel = QWebChannel()
        self.bridge = Bridge()
        self.channel.registerObject('bridge', self.bridge)
        self.web_view.page().setWebChannel(self.channel)
        self.bridge.pageNumber.connect(self.user_comment)

    def add_bookmark(self):
        js_code = """
        new QWebChannel(qt.webChannelTransport, function(channel){
            window.bridge = channel.objects.bridge;
            var number = PDFViewerApplication.pdfViewer.currentPageNumber;
            bridge.cuePageNum(number);
        })();
        """
        self.web_view.page().runJavaScript(js_code)

    def user_comment(self, number):
        print('test page num', number)
        comment_dialog = QInputDialog(self)
        comment_dialog.setOption(QInputDialog.UsePlainTextEditForTextInput)
        comment_dialog.setWindowIcon(QIcon("assets/bookmark_icon.png"))
        comment_dialog.setWindowTitle('Add Bookmark')
        comment_dialog.setLabelText('Enter comment for bookmark:')
        comment_dialog.resize(100,300)
        comment_dialog.setOkButtonText('Add')

        if comment_dialog.exec() == QInputDialog.Accepted:
            selected_text = self.web_view.page().selectedText()
            recorded_comment = comment_dialog.textValue()
            bookmark = {
                'file': self.file_path,
                'page': number, 
                'text': selected_text, 
                'comment': recorded_comment                
            }
            print('bookmark dict obj:', bookmark)
            self.bookmark_signal.emit(bookmark)

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
        self.file_path = file_path
        full_url = QUrl(f'file:///{self.pdf_js_path}?file=file:///{encoded_file_path}#page={self.current_page}')
        #print('this is full url:', full_url.toString())
        self.web_view.load(full_url)
