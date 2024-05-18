# Copyright (c) EGOGE - All Rights Reserved.
# This software may be used and distributed according to the terms of the Apache-2.0 license.
from PyQt5.QtCore import QObject, Qt, QSize, QTimer
from PyQt5.QtWidgets import QScrollArea, QVBoxLayout, QWidget, QPushButton, QDockWidget, QHBoxLayout, QTextEdit
from PyQt5.QtGui import QIcon, QFont, QPixmap

from langchain_community.vectorstores import Chroma

from retrieval_qa import create_retrieval_qa
from prompt_info import PromptInfo
from models.model_info import ModelInfo
from .study_task import TaskWorker
from .study_stream_error import StudyStreamException
from .study_message_type import StudyMessageType
from .study_message_widget import StudyMessageWidget

class StudyAssistorPanel(QDockWidget):
    def __init__(self, parent: QObject, system_prompt: PromptInfo, app_config, color_scheme, asserts_path: str, db: Chroma, model_info: ModelInfo, verbose: bool, logging):
        super().__init__(parent=parent)
        self.parent = parent
        self.asserts_path = asserts_path
        self.color_scheme = color_scheme
        self.app_config = app_config
        self.docs_db = db
        self.system_prompt = system_prompt
        self.model_info = model_info
        self.logging = logging
        self.verbose = verbose
        self.timer = None
        self.rotate_icon_angle = 0
        self.create_assistor()
        self.initUI()

    def create_assistor(self):
        dic = self.docs_db.get()["ids"]
        documents_count = len(dic)
        self.logging.info(f"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\nLoaded the vectorstore with {documents_count} documents.\nLLM model name: {self.model_info.model_name}.\nSystem Prompt:\n---\n{self.system_prompt}\n---\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")  
        self.qa_service = create_retrieval_qa(model_info=self.model_info, prompt_info=self.system_prompt, vectorstore=self.docs_db)
        if self.qa_service is None:
            raise StudyStreamException(f"Failed to initialize the retrieval framework for the vectorstore: {self.docs_db}.")      
    
    def initUI(self):
        self.setAllowedAreas(Qt.RightDockWidgetArea)

        chat_widget = QWidget()  # This will hold all the chat components
        chat_layout = QVBoxLayout(chat_widget)
        chat_layout.setContentsMargins(10, 10, 10, 10)
        chat_layout.setSpacing(10)

        # Scroll area for chat display
        self.scroll_area = QScrollArea(chat_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_layout.setSpacing(10)
        self.scroll_area.setWidget(self.scroll_content)
        chat_layout.addWidget(self.scroll_area)

        # Input area
        input_area = QWidget()
        input_area_layout = QHBoxLayout(input_area)
        input_area_layout.setContentsMargins(10, 10, 10, 10)
        input_area_layout.setSpacing(10)
        input_area_layout.setAlignment(Qt.AlignTop)  # Ensure the input area is aligned at the top

        # CSS for chat
        print(f"Scheme: {self.color_scheme}")
        self.icon_css = self.color_scheme['chat-icon-css']
        self.ai_icon_css = self.color_scheme['ai-icon-css']
        self.user_message = self.color_scheme['user-message-css']
        self.ai_message = self.color_scheme['ai-message-css']
        self.user_message = self.color_scheme['user-message-css']
        self.datetime_css = self.color_scheme['datetime-css']
        self.datetime_user_css = self.color_scheme['datetime-user-css']

        self.attach_button = QPushButton()
        icon_path = self.asserts_path + self.app_config['file_attach_icon']
        self.attach_button.setIcon(QIcon(icon_path))
        self.attach_button.setIconSize(QSize(32, 32))  # Increased icon size
        self.attach_button.setFixedSize(48, 48)
        self.attach_button.setStyleSheet(self.icon_css)
        input_area_layout.addWidget(self.attach_button, alignment=Qt.AlignTop)

        self.chat_input = QTextEdit()
        self.chat_input.setPlaceholderText(self.app_config['chat_ask_placeholder'])
        self.chat_input.setFont(QFont(self.app_config['chat_font'], self.app_config['chat_font_size']))
        self.chat_input.setStyleSheet(self.color_scheme["chat-text-css"])
        self.chat_input.setFixedHeight(100)  # Limit height to 20% of the window height
        self.chat_input.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        input_area_layout.addWidget(self.chat_input)

        self.send_button = QPushButton()
        icon_path = self.asserts_path + self.app_config['send_button_icon']
        self.rotating_send_button_icon = QPixmap(icon_path) 
        self.send_button_icon = QIcon(icon_path) 
        self.send_button.setIcon(self.send_button_icon)
        self.send_button.setIconSize(QSize(32, 32))  # Increased icon size
        self.send_button.setFixedSize(48, 48)
        self.send_button.setStyleSheet(self.icon_css)
        self.send_button.clicked.connect(self.sendMessage)
        input_area_layout.addWidget(self.send_button, alignment=Qt.AlignTop)

        # Add input_area to main_layout
        chat_layout.addWidget(input_area, alignment=Qt.AlignBottom)
        
        self.setWidget(chat_widget)
    
    def sendMessage(self):
        self.set_chat_state(enabled=False)
        question = self.chat_input.toPlainText()
        self.add_message(
            message=question, 
            message_type=StudyMessageType.USER, 
            text_css=self.user_message, 
            icon_css=self.icon_css,
            datetime_css=self.datetime_user_css
        )
        self.chat_input.clear()
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate_icon)
        self.timer.start(500)
        self.async_task_question(question=question)  
    
    def async_task_question(self, question: str):   
        self.file_task = TaskWorker(self.ask_ai, question)
        self.file_task.finished.connect(lambda result: self.on_task_complete(result))
        self.file_task.error.connect(lambda error: self.on_task_error(error))
        self.file_task.run()    
    
    def rotate_icon(self):    
        new_icon, self.rotate_icon_angle = StudyMessageType.rotate_icon(
            rotating_icon=self.rotating_send_button_icon, 
            rotate_icon_angle=self.rotate_icon_angle
        )
        print(f"{new_icon} - {self.rotate_icon_angle}")
        self.send_button.setIcon(new_icon)     
        
    def ask_ai(self, question: str):
        return self.qa_service(question)    

    def on_task_complete(self, results):            
        answer, docs = results["result"], results["source_documents"] 
        self.add_message(
            message=answer, 
            message_type=StudyMessageType.SYSTEM, 
            text_css=self.ai_message, 
            icon_css=self.ai_icon_css,
            datetime_css=self.datetime_css
        )    
        if self.verbose:
            log_message = f"=============\n{answer}\n"
            for document in docs:
                log_message += f">>> {document.metadata['source']}:{document.page_content}\n"
            log_message += "============="
            self.logging.info(log_message)
        else:            
            self.logging.info(f"Got the answer from ai.")
        
        self.set_chat_state(enabled=True)        

    def on_task_error(self, error):
        self.logging.info(f"Failed to get an answer from ai: {error}")
        self.set_chat_state(enabled=True)

    def set_chat_state(self, enabled: bool):
        if enabled:
            if self.timer:
                self.timer.stop()
                self.timer = None   
            self.rotate_icon_angle = 0      
            self.attach_button.setDisabled(False)
            self.send_button.setDisabled(False)
            self.send_button.setIcon(self.send_button_icon)
            self.chat_input.setPlaceholderText(self.app_config['chat_ask_placeholder'])
            self.chat_input.setEnabled(True)
        else: 
            self.attach_button.setDisabled(True)
            self.send_button.setDisabled(True)
            self.chat_input.setPlaceholderText(self.app_config['chat_waiting_message'])
            self.chat_input.setEnabled(False)


    def add_message(self, message: str, message_type: StudyMessageType, text_css: str, icon_css: str, datetime_css: str):
        icon = message_type.get_icon(app_config=self.app_config, asserts_path=self.asserts_path)
        message_widget = StudyMessageWidget(message=message, icon=icon, text_css=text_css, icon_css=icon_css, datetime_css=datetime_css)
        self.scroll_layout.addWidget(message_widget)
        self.scroll_content.adjustSize()