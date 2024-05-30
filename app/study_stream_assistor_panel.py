# Copyright (c) EGOGE - All Rights Reserved.
# This software may be used and distributed according to the terms of the Apache-2.0 license.
from datetime import datetime
from typing import Dict
import json
import pytz
from PySide6.QtCore import QObject, Qt, QSize, QTimer
from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget, QPushButton, QDockWidget, QHBoxLayout, QTextEdit
from PySide6.QtGui import QIcon, QFont, QPixmap

from langchain_community.vectorstores import Chroma

from models.retrieval_qa import create_retrieval_qa
from db.study_stream_dao import update_note
from models.prompt_info import PromptInfo
from models.model_info import ModelInfo
from .study_stream_task import StudyStreamTaskWorker
from .study_stream_error import StudyStreamException
from .study_stream_chat_icon_type import StudyStreamChatIconType
from .study_stream_message_widget import StudyStreamMessageWidget
from study_stream_api.study_stream_subject import StudyStreamSubject
from study_stream_api.study_stream_message import StudyStreamMessage
from study_stream_api.study_stream_note import StudyStreamNote
from study_stream_api.study_stream_message_type import StudyStreamMessageType

DEFAULT_STUDENT_NOTE = "Student Note"

class StudyStreamAssistorPanel(QDockWidget):
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
        self.messages = []
        self.study_target = None
        self.create_assistor()
        self.initUI()

    def create_assistor(self):
        dic = self.docs_db.get()["ids"]
        documents_count = len(dic)
        self.logging.info(f"\n>>>>>>>>>>>>>\nLoaded the vectorstore with {documents_count} documents.\nLLM model name: {self.model_info.model_name}.\nSystem Prompt:\n---\n{self.system_prompt}\n---\n<<<<<<<<<<<<")  
        self.qa_service = create_retrieval_qa(model_info=self.model_info, prompt_info=self.system_prompt, vectorstore=self.docs_db)
        if self.qa_service is None:
            raise StudyStreamException(f"Failed to initialize the retrieval framework for the vectorstore: {self.docs_db}.")      
    
    def initUI(self):
        self.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)

        chat_widget = QWidget()  # This will hold all the chat components
        chat_layout = QVBoxLayout(chat_widget)
        chat_layout.setContentsMargins(5, 5, 5, 5)
        chat_layout.setSpacing(5)

        self.title_lable = QLabel(DEFAULT_STUDENT_NOTE)
        self.title_lable.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        chat_layout.addWidget(self.title_lable)

        # Scroll area for chat display
        self.scroll_area = QScrollArea(chat_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(self.color_scheme["main-css"])
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_layout.setSpacing(5)
        self.scroll_area.setWidget(self.scroll_content)
        chat_layout.addWidget(self.scroll_area)

        # Input area
        input_area = QWidget()
        input_area.setStyleSheet(self.color_scheme['toolbar-css'])
        input_area_layout = QHBoxLayout(input_area)
        input_area_layout.setContentsMargins(10, 10, 10, 10)
        input_area_layout.setSpacing(10)
        input_area_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # CSS for chat
        self.icon_css = self.color_scheme['chat-icon-css']
        self.ai_icon_css = self.color_scheme['ai-icon-css']        
        self.comment_message = self.color_scheme['comment-css']        
        self.user_message = self.color_scheme['user-message-css']
        self.ai_message = self.color_scheme['ai-message-css']
        self.datetime_css = self.color_scheme['datetime-css']
        self.datetime_user_css = self.color_scheme['datetime-user-css']

        self.button_css = self.color_scheme['object-button-css']
        self.button_hover_css = self.color_scheme['object-button-hover-css']
        self.button_pressed_css = self.color_scheme['object-button-pressed-css']
        self.disabled_button_css = self.color_scheme['disabled-object-button-css']
        self.enabled_css = f"""
            QPushButton {{
                {self.button_css} 
            }}
            QPushButton:hover {{
                {self.button_hover_css}   
            }}
            QPushButton:pressed {{
                {self.button_pressed_css}
            }}
        """
        self.disbaled_css = f"""
            QPushButton {{
                {self.disabled_button_css} 
            }}
            QPushButton:hover {{}}
            QPushButton:pressed {{}}
        """

        self.save_chat_button = QPushButton()
        icon_path = self.asserts_path + self.app_config['save_chat_icon']
        self.save_chat_button.setIcon(QIcon(icon_path))
        self.save_chat_button.setIconSize(QSize(32, 32))  # Increased icon size
        self.save_chat_button.setFixedSize(48, 48)
        self.save_chat_button.clicked.connect(self.save_chat)
        self.update_save_chat_button(is_enabled=False)
        input_area_layout.addWidget(self.save_chat_button, alignment=Qt.AlignmentFlag.AlignTop)

        self.chat_input_area = QTextEdit()
        self.chat_input_area.setPlaceholderText(self.app_config['chat_ask_placeholder'])
        self.chat_input_area.setFont(QFont(self.app_config['chat_font'], self.app_config['chat_font_size']))
        self.chat_input_area.setStyleSheet(self.color_scheme["chat-text-css"])
        self.chat_input_area.setFixedHeight(100)  # Limit height to 20% of the window height
        self.chat_input_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        input_area_layout.addWidget(self.chat_input_area)

        self.send_button = QPushButton()
        icon_path = self.asserts_path + self.app_config['send_button_icon']
        self.rotating_send_button_icon = QPixmap(icon_path) 
        self.send_button_icon = QIcon(icon_path) 
        self.send_button.setIcon(self.send_button_icon)
        self.send_button.setIconSize(QSize(32, 32))  # Increased icon size
        self.send_button.setFixedSize(48, 48)
        self.send_button.setStyleSheet(self.enabled_css)
        self.send_button.setToolTip("Send your question!")
        self.send_button.clicked.connect(self.send_message)
        input_area_layout.addWidget(self.send_button, alignment=Qt.AlignmentFlag.AlignTop)

        # Add input_area to main_layout
        chat_layout.addWidget(input_area, alignment=Qt.AlignmentFlag.AlignBottom)
        
        self.setWidget(chat_widget)

    def set_study_taget(self, target: StudyStreamSubject):
        if target and (not self.study_target or target.id != self.study_target): 
            clean_chat = True
            if not self.study_target:
                clean_chat = False
            self.study_target = target               
            self.title_lable.setText(self.study_target.class_name)
            self.load_student_note(self.study_target.note, clean_chat=clean_chat)
            self.set_chat_state(is_chat_enabled=True)
        else:     
            self.title_lable.setText(DEFAULT_STUDENT_NOTE)

    def load_student_note(self, note: StudyStreamNote, clean_chat: bool):
        if clean_chat:
            self.clear_chat() 
        if note:
            self.messages = note.to_messages()
            for message in self.messages:
                if message.type == StudyStreamMessageType.QUESTION.value:
                    self.add_message(
                        message=message.content,
                        message_type=StudyStreamChatIconType.USER,
                        text_css=self.user_message,
                        icon_css=self.icon_css,
                        datetime_css=self.datetime_user_css
                    )
                elif message.type == StudyStreamMessageType.ANSWER.value:
                    self.add_message(
                        message=message.content,
                        message_type=StudyStreamChatIconType.SYSTEM, 
                        text_css=self.ai_message, 
                        icon_css=self.ai_icon_css,
                        datetime_css=self.datetime_css
                    ) 
        else:
            self.messages = []      

    def add_bookmark(self, bookmark: Dict):
        print(f'BOOKMARK: {bookmark}')
        # Convert dictionary to a JSON-formatted string with indentation
        dict_str = json.dumps(bookmark, indent=4)

        # Construct a markdown-friendly string
        if bookmark['comment']:
            bookmark_markdown = f"""
            Bookmark at the page #{bookmark['page']} of **{bookmark['file'].split('/')[-1]}**
              - Selected Text: _{bookmark['text']}_
              - Comment: _{bookmark['comment']}_
            """
        else:    
            bookmark_markdown = f"""            
            Bookmark at the page #{bookmark['page']} of **{bookmark['file'].split('/')[-1]}**
              - Selected Text: _{bookmark['text']}_
            """

        new_message = StudyStreamMessage(
            type=StudyStreamMessageType.BOOKMARK,
            content=dict_str,
            creation_time=datetime.now(tz=pytz.utc)
        )
        
        self.messages.append(new_message)          
        self.update_save_chat_button(is_enabled=True)
        self.add_message(
            message=bookmark_markdown, 
            message_type=StudyStreamChatIconType.BOOKMARK, 
            text_css=self.comment_message, 
            icon_css=self.icon_css,
            datetime_css=self.datetime_user_css
        ) 
    
    def save_chat(self):
        print(f"save_chat: {self.study_target} - {self.messages}")
        if self.study_target and self.messages and len(self.messages) > 0:
            json_txt = StudyStreamNote.messages_to_json(messages=self.messages)
            print(f"JSON: {json_txt}")         
            updated_class = update_note(updated_class=self.study_target, note=json_txt)
            if updated_class:                     
                self.update_save_chat_button(is_enabled=False)
    
    def send_message(self):
        self.set_chat_state(is_chat_enabled=False)
        question = self.chat_input_area.toPlainText()
        self.send_question(question=question)

    def send_question(self, question: str)-> bool:    
        if self.timer:
            return False
        new_message = StudyStreamMessage(
            type=StudyStreamMessageType.QUESTION,
            content=question,
            creation_time=datetime.now(tz=pytz.utc)
        )
        self.messages.append(new_message)
        self.update_save_chat_button(is_enabled=True)
        self.add_message(
            message=question, 
            message_type=StudyStreamChatIconType.USER, 
            text_css=self.user_message, 
            icon_css=self.icon_css,
            datetime_css=self.datetime_user_css
        )
        self.chat_input_area.clear()
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate_icon)
        self.timer.start(500)
        self.async_task_question(question=question)  

        return True
    
    def async_task_question(self, question: str):   
        self.file_task = StudyStreamTaskWorker(self.ask_ai, question)
        self.file_task.finished.connect(lambda result: self.on_task_complete(result))
        self.file_task.error.connect(lambda error: self.on_task_error(error))
        self.file_task.run()    
    
    def rotate_icon(self):    
        new_icon, self.rotate_icon_angle = StudyStreamChatIconType.rotate_icon(
            rotating_icon=self.rotating_send_button_icon, 
            rotate_icon_angle=self.rotate_icon_angle
        )
        self.send_button.setIcon(new_icon)     
        
    def ask_ai(self, question: str):
        return self.qa_service(question)    

    def on_task_complete(self, results):            
        answer, docs = results["result"], results["source_documents"]          
        new_message = StudyStreamMessage(
            type=StudyStreamMessageType.ANSWER,
            content=answer,
            creation_time=datetime.now(tz=pytz.utc)
        )
        self.messages.append(new_message)          
        self.update_save_chat_button(is_enabled=True)
        self.add_message(
            message=answer, 
            message_type=StudyStreamChatIconType.SYSTEM, 
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
        
        self.set_chat_state(is_chat_enabled=True)        

    def on_task_error(self, error):
        self.logging.info(f"Failed to get an answer from ai: {error}")
        self.set_chat_state(is_chat_enabled=True)        
    
    def update_save_chat_button(self, is_enabled: bool):
        if is_enabled and self.study_target and self.messages and len(self.messages) > 0:
            self.save_chat_button.setDisabled(False)
            self.save_chat_button.setStyleSheet(self.enabled_css)
            self.save_chat_button.setToolTip("Save your chat history!")
        else:        
            self.save_chat_button.setDisabled(True) 
            self.save_chat_button.setStyleSheet(self.disbaled_css)
            self.save_chat_button.setToolTip("Your chat history is saved!")

    def set_chat_state(self, is_chat_enabled: bool):
        if is_chat_enabled:
            if self.timer:
                self.timer.stop()
                self.timer = None   
            self.rotate_icon_angle = 0      
            self.update_save_chat_button(is_enabled=True)
            self.send_button.setDisabled(False)
            self.send_button.setIcon(self.send_button_icon)
            self.chat_input_area.setPlaceholderText(self.app_config['chat_ask_placeholder'])
            self.chat_input_area.setEnabled(True)
        else:   
            self.update_save_chat_button(is_enabled=False)
            self.send_button.setDisabled(True)
            self.chat_input_area.setPlaceholderText(self.app_config['chat_waiting_message'])
            self.chat_input_area.setEnabled(False)

    def add_message(self, message: str, message_type: StudyStreamMessageType, text_css: str, icon_css: str, datetime_css: str):
        icon = message_type.get_icon(app_config=self.app_config, asserts_path=self.asserts_path)
        message_widget = StudyStreamMessageWidget(message=message, icon=icon, text_css=text_css, icon_css=icon_css, datetime_css=datetime_css)
        self.scroll_layout.addWidget(message_widget)        
        self.scroll_to_bottom(widget_height=message_widget.height())

    def scroll_to_bottom(self, widget_height: int):
        # Scroll the vertical scrollbar to the maximum position
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum() + widget_height + 50
        )
        self.scroll_area.show()

    def clear_chat(self):
        while  self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()    
