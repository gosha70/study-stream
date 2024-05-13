# Copyright (c) EGOGE - All Rights Reserved.
# This software may be used and distributed according to the terms of the Apache-2.0 license.
import sys
import os
import argparse
import logging
import json
from retrieval_constants import CURRENT_DIRECTORY

from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow)
from PyQt5.QtCore import Qt

from models.model_info import ModelInfo
from embeddings.embeddings_constants import DEFAULT_COLLECTION_NAME
from embeddings.embedding_database import load_vector_store
from embeddings.unstructured.document_splitter import DocumentSplitter

from prompt_info import PromptInfo
from .study_classes_panel import StudyClassesPanel
from .study_document_view import StudyDocumentView
from .study_stream_error import StudyStreamException
from .study_assistor_panel import StudyAssistorPanel


class StudyStreamApp(QMainWindow):
    def __init__(self, arguments, logging):
        super().__init__()
        # Set the working directory to the script's directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        self.current_dir = os.getcwd()
        with open(self.current_dir + '/app_config.json', 'r') as file:
            self.app_config = json.load(file)  
        with open(self.current_dir + '/color_schemes/dark-color-scheme.json', 'r') as file:
            self.color_scheme = json.load(file)  
        self.verbose=arguments.verbose
        self.logging = logging        
        self.start_model(args=arguments)

        self.initUI()
        self.doc = None
        self.pdf_files = []
        self.page_index = 0  # Initialize page_index here
    
    def start_model(self, args):
        print('start_model')
        # Init ML/AI models
        self.next_question_delay = self.app_config["next_question_delay"]
        # The number of seconds passed b/w questions
        if self.next_question_delay is None or self.next_question_delay < 1:
            self.next_question_delay = 1
        self.logging.info(f"Minimum wait in seconds b/w questions: {self.next_question_delay}")

        # System prompt muat be specified for embeddings
        self.app_system_prompt = self.app_config["system_prompt"]
        self.logging.info(f"System prompts: {self.app_system_prompt}")

        self.model_info = ModelInfo() # DEFAULT_MODEL_NAME = "hkunlp/instructor-large" 
        app_system_prompt = self.app_config["system_prompt"]    
        self.prompt_info = PromptInfo(system_prompt=app_system_prompt, template_type=args.prompt_template, use_history=args.history)

        self.logging.info(f"Input arguments:\n===\n{args}\n===\nLoading the vectorstore from {args.persist_directory} ...")
        self.docs_db = load_vector_store(
            model_name=self.model_info.model_name, 
            collection_name=args.collection_name, 
            persist_directory=args.persist_directory
        )
        
        if self.docs_db is None:
            raise StudyStreamException(f"Failed to load the vectorstore from {args.persist_directory}.")  
        else:
            self.document_splitter = DocumentSplitter(logging)

    def initUI(self):
        self.setWindowTitle("Study Stream")
        self.showMaximized()

        # Left Panel: Toolbar and List of PDFs
        left_panel = StudyClassesPanel(
            parent=self, 
            app_config=self.app_config, 
            color_scheme=self.color_scheme["left_panel"],
            asserts_path=self.current_dir,
            db=self.docs_db,
            logging=self.logging
        )

        # Central Panel: Display PDF
        central_panel = StudyDocumentView(
            parent=self, 
            app_config=self.app_config, 
            color_scheme=self.color_scheme["center_panel"],
            asserts_path=self.current_dir,
            verbose=self.verbose,
            logging=self.logging
        )

        # Right Panel: Chat with LLM
        right_panel = StudyAssistorPanel(
            parent=self, 
            system_prompt=self.prompt_info,
            app_config=self.app_config, 
            color_scheme=self.color_scheme["left_panel"],
            asserts_path=self.current_dir,
            db=self.docs_db,
            model_info=self.model_info, 
            verbose=self.verbose,
            logging=self.logging
        )
       
        self.addDockWidget(Qt.LeftDockWidgetArea, left_panel)
        self.setCentralWidget(central_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, right_panel)

    def show(self):
        super().show() 

def process_arguments():
    # Create the parser
    parser = argparse.ArgumentParser(description="Study Stream Application")

    parser.add_argument(
        '--persist_directory', 
        type=str, 
        help='The path to the directory where the vectorstore will be persisted. Defaults to the root directory.', 
        default=CURRENT_DIRECTORY
    )
    parser.add_argument(
        '--collection_name', 
        type=str, 
        help='The name of vectorestore.', 
        default=DEFAULT_COLLECTION_NAME
    )
    parser.add_argument(
        '--prompt_template', 
        type=str, 
        help='(Optional) the promp template type: "llama", "mistral"',
        default=None
    )
    parser.add_argument(
        '--history', 
        type=bool, 
        help='(Optional) The flag indicates if LLM supports the propmpt history.', 
        default=False
    )
    parser.add_argument(
        '--verbose', 
        type=bool, 
        help='(Optional) The flag indicates that the results must be printed out to the console.', 
        default=False
    )
    
    # Parse the arguments
    return parser.parse_args()

if __name__ == '__main__':
    # Set the logging level to INFO    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Parse the arguments
    args = process_arguments()
    verbose = args.verbose   

    app = QApplication(sys.argv)
    main_app = StudyStreamApp(arguments=args, logging=logging)
    main_app.show()
    sys.exit(app.exec_())
 