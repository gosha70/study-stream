# Copyright (c) EGOGE - All Rights Reserved.
# This software may be used and distributed according to the terms of the Apache-2.0 license.
from PyQt5.QtCore import QObject, Qt
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QTextEdit, QDockWidget)

from langchain_community.vectorstores import Chroma

from retrieval_qa import create_retrieval_qa
from prompt_info import PromptInfo
from models.model_info import ModelInfo
from .study_stream_error import StudyStreamException

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

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        chat_layout.addWidget(self.chat_display)

        self.chat_input = QTextEdit()
        self.chat_input.setFixedHeight(100)
        chat_layout.addWidget(self.chat_input)

        send_button = QPushButton('Send')
        send_button.clicked.connect(self.sendMessage)
        chat_layout.addWidget(send_button)

        self.setWidget(chat_widget) 

    def sendMessage(self):
        question = self.chat_input.toPlainText()
        self.chat_display.append("You: " + question)
        results = self.qa_service(question)
        answer, docs = results["result"], results["source_documents"]
        self.logging.info(f"Got the answer on the question:\n {question}.") 
        if self.verbose: 
            log_message = f"=============\n{answer}\n"
            for document in docs:
                log_message = log_message +  f">>> {document.metadata['source']}:{document.page_content}\n"
            log_message = log_message + "=============" 
            self.logging.info(log_message)
        
        # Placeholder for LLM response
        self.chat_display.append("LLM: " + answer)
        self.chat_input.clear()