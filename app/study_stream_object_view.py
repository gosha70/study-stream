# Copyright (c) EGOGE - All Rights Reserved.
# This software may be used and distributed according to the terms of the Apache-2.0 license.
from typing import List
from PySide6.QtWidgets import (QHBoxLayout,  QToolTip, QScrollArea, QPushButton, QGridLayout, QLineEdit, 
                              QSpacerItem, QWidget, QLabel, QFrame, QVBoxLayout, QDateTimeEdit, QSizePolicy)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import QObject, QSize, Qt, QDateTime, QTimer

from langchain_community.vectorstores import Chroma
from embeddings.unstructured.document_splitter import DocumentSplitter
from embeddings.embedding_database import add_file_content_to_db
from db.study_stream_dao import update_document, update_class, update_school
from .study_stream_task import StudyStreamTaskWorker
from .study_stream_message_type import StudyStreamMessageType
from study_stream_api.study_stream_document import StudyStreamDocument
from study_stream_api.study_stream_school import StudyStreamSchool
from study_stream_api.study_stream_subject import StudyStreamSubject
from study_stream_api.study_stream_school_type import StudyStreamSchoolType
from study_stream_api.study_stream_document_status import StudyStreamDocumentStatus
from embeddings.unstructured.file_type import FileType


class HoverLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setToolTip(text)

    def enterEvent(self, event):
        QToolTip.showText(self.mapToGlobal(event.pos()), self.text(), self)

    def leaveEvent(self, event):
        QToolTip.hideText()

class StudyStreamObjectView(QWidget):
    def __init__(
            self, 
            parent: QObject,
            dependent_object: QLabel, 
            app_config,  
            color_scheme, 
            current_dir: str, 
            db: Chroma, 
            load_chat_lambda,
            logging):
        super().__init__(parent)
        self.parent = parent
        self.dependent_object = dependent_object
        self.current_dir = current_dir   
        self.app_config = app_config 
        self.color_scheme = color_scheme
        self.logging = logging
        self.db = db
        self.load_chat_lambda = load_chat_lambda
        self.document_splitter = DocumentSplitter(logging)
        self.document_in_progress = None
        self.study_doc = None
        self.study_class = None
        self.study_school = None
        self.file_in_progress = None 
        self.file_task = None
        self.on_save_item = None
        self.initUI()

    def initUI(self):
        self.setStyleSheet(self.color_scheme['card-css'])   
        self.control_css = self.color_scheme['control-css']
        self.readonly_control_css = self.color_scheme['control-readonly-css']
        self.label_css = self.color_scheme['label-css']
        self.icon_css = self.color_scheme['icon-css']

        self.datetime_css = f"""
            QDateTimeEdit {{
                {self.control_css} 
            }}
            QDateTimeEdit::up-button,
            QDateTimeEdit::down-button {{
                width: 0;
                height: 0;
            }}
        """
        self.readonly_datetime_css = f"""
            QDateTimeEdit {{
                {self.readonly_control_css} 
            }}
            QDateTimeEdit::up-button,
            QDateTimeEdit::down-button {{
                width: 0;
                height: 0;
            }}
        """

        self.default_icon = QIcon(self.current_dir + self.app_config['default_view_icon'])
        self.class_icon_path = self.current_dir + self.app_config['class_view_icon']
        self.class_icon = QIcon(self.class_icon_path)
        self.doc_icon = QIcon(self.current_dir + self.app_config['document_view_icon'])
        self.school_icon = QIcon(self.current_dir + self.app_config['school_view_icon'])

        self.high_school_icon = QIcon(self.current_dir + self.app_config['high_school_icon'])
        self.college_icon = QIcon(self.current_dir + self.app_config['college_school_icon'])
        self.university_icon = QIcon(self.current_dir + self.app_config['university_school_icon'])
        self.course_icon = QIcon(self.current_dir + self.app_config['course_school_icon'])
        self.start_chat_icon = QIcon(self.current_dir + self.app_config['start_chat_icon'])

        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.title_button = QPushButton()
        self.title_button.setCheckable(True)
        self.title_button.setChecked(False)
        self.title_button.setDisabled(True)
        self.title_button.setIcon(self.default_icon)
        self.title_button.setStyleSheet(self.color_scheme['title-css'])
        icon_size = 40
        self.title_button.setIconSize(QSize(icon_size, icon_size))
        self.title_button.setText(self.app_config['default_object_view_text'])
        self.title_button.clicked.connect(self.on_click)
        self.main_layout.addWidget(self.title_button)

        self.content_area = QFrame()
        self.content_area.setStyleSheet(self.color_scheme['card-grid-css'])
        self.content_area.setVisible(False)
        self.content_area_layout = QVBoxLayout()
        self.content_area.setLayout(self.content_area_layout)
        self.main_layout.addWidget(self.content_area)

        self.disabled_delete_icon = QIcon(self.current_dir + self.app_config['disbaled_delete_object_icon']) 
        self.delete_icon = QIcon(self.current_dir + self.app_config['delete_object_icon']) 
        self.load_icon = QIcon(self.current_dir + self.app_config['load_object_icon']) 
        self.loading_icon_path = self.current_dir + self.app_config['loading_object_icon']               
        self.rotating_icon = QPixmap(self.loading_icon_path)  
        self.loading_icon = QIcon(self.loading_icon_path)
        self.save_icon = QIcon(self.current_dir + self.app_config['save_object_icon']) 

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
   
        icon_size = QSize(64, 64)

        button_layout = QHBoxLayout()

        self.start_chat_button = QPushButton()
        self.start_chat_button.setIcon(self.start_chat_icon)
        self.start_chat_button.setIconSize(icon_size) 
        self.start_chat_button.setStyleSheet(self.enabled_css)
        self.start_chat_button.clicked.connect(self.start_chat)    
        self.start_chat_button.setVisible(False)     
        self.start_chat_button.setToolTip("Load the student note")  

        self.save_button = QPushButton()
        self.save_button.setIcon(self.save_icon)
        self.save_button.setIconSize(icon_size) 
        self.save_button.setStyleSheet(self.enabled_css)
        self.save_button.clicked.connect(self.save_action)    
        self.save_button.setVisible(False)     
        self.save_button.setToolTip("Save this entry in the database")  

        self.llm_button = QPushButton()
        self.llm_button.setIcon(self.load_icon)
        self.llm_button.setIconSize(icon_size) 
        self.llm_button.setStyleSheet(self.disbaled_css)
        self.llm_button.clicked.connect(self.process_document)    
        self.llm_button.setVisible(False)     
        self.llm_button.setToolTip("Analyze the document with AI")  

        self.delete_button = QPushButton()   
        self.delete_button.setIcon(self.delete_icon)
        self.delete_button.setIconSize(icon_size) 
        self.delete_button.setStyleSheet(self.disbaled_css)
        self.delete_button.clicked.connect(self.delete_action)
        self.delete_button.setVisible(False)

        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))       
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.llm_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.start_chat_button)
        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))   
        
        self.main_layout.addLayout(button_layout)

        self.setLayout(self.main_layout)   

    def start_chat(self):
       if self.study_class:
          print(f"start_chat({self.study_class})")
          self.load_chat_lambda(self.study_class)

    def save_action(self):
        if self.study_doc:
            print(f"Saving Document: {self.study_doc.name}")
            updated_doc = update_document(updated_document=self.study_doc)
            if updated_doc:   
                self.study_doc = updated_doc 
                if self.on_save_item:
                    self.on_save_item(name=self.study_doc.name, status=self.study_doc.status_enum)
        elif self.study_class:
            print(f"Saving Class: {self.study_class.class_name}")
            self.study_class.class_name = self.title_button.text()
            updated_class = update_class(updated_class=self.study_class)
            if updated_doc:   
                self.study_class = updated_class 
                if self.on_save_item:
                    self.on_save_item(name=self.study_class.class_name, status=None)
        elif self.study_school:
            print(f"Saving School: {self.study_school.name}")
            updated_school = update_school(updated_school=self.study_school)
            if updated_school:   
                self.study_school = updated_school  
                if self.on_save_item:
                    self.on_save_item(name=self.study_school.name, status=None)            
        else:
            self.logging.warn(f"No item is available for save!!!")
            
    def delete_action(self):
        pass       

    def on_click(self):         
        checked = self.title_button.isChecked()
        self.update_content(is_enabled=checked)

    def update_content(self, is_enabled: bool):   
        self.content_area.setVisible(is_enabled) 
        self.dependent_object.setVisible(not is_enabled)        
        self.save_button.setVisible(is_enabled) 
        if self.study_class:
            self.start_chat_button.setVisible(is_enabled) 
        else:   
            self.start_chat_button.setVisible(False)   
        self.delete_button.setVisible(is_enabled)     
        self.show_llm_button(is_enabled) 

    def show_llm_button(self, is_visible: bool):
        if is_visible:  
            if self.study_doc:          
                if self.study_doc.status == StudyStreamDocumentStatus.NEW.value:
                    self.llm_button.setVisible(True)
                    self.llm_button.setDisabled(False)
                    self.llm_button.setStyleSheet(self.enabled_css)
                    self.llm_button.setIcon(self.load_icon)
                elif self.study_doc.status == StudyStreamDocumentStatus.IN_PROGRESS.value:
                    self.llm_button.setVisible(True)
                    self.llm_button.setDisabled(True)
                    self.llm_button.setStyleSheet(self.disbaled_css)
                    self.llm_button.setIcon(self.loading_icon)            
            elif self.document_in_progress:
                self.llm_button.setToolTip(f"Please wait ! Analyzing {self.document_in_progress.name} ...")  
                self.llm_button.setDisabled(False)
                self.llm_button.setVisible(True)                
            else:
                self.llm_button.setVisible(False)
        else:
            self.llm_button.setVisible(False)

    def display_school(self, school: StudyStreamSchool, on_save_item):
        self.on_save_item = on_save_item
        self.reset_content()
        if school:
            self.study_school = school
            self.title_button.setText(school.name)
            self.title_button.setIcon(self.class_icon)

            school_icon = self.get_school_type(school_type=school.school_type_enum)

            fields_grid = QGridLayout()
            self.create_document_field(fields_grid, "School Name:", school.name, 0, 
                                       setter_lambda=lambda text: setattr(school, 'name', text),is_read_only=False, field_icon=school_icon)
            self.create_datetime_field(fields_grid, "Start Date:", school.start_date, 1, 
                                       lambda qdatetime: setattr(school, 'start_date', qdatetime.toPython()),is_read_only=False)
            self.create_datetime_field(fields_grid, "Graduation Date:", school.finish_date, 2, 
                                       lambda qdatetime: setattr(school, 'finish_date', qdatetime.toPython()),is_read_only=False)
            self.content_area_layout.addLayout(fields_grid)
            self.add_subject_card(subjects=school.subjects)
            self.enable_content()     
            self.update_content(is_enabled=True)     
            self.title_button.setDisabled(True) 

    def add_subject_card(self, subjects: List[StudyStreamSubject]):
        scroll_area = QScrollArea()
        scroll_area.setStyleSheet(self.color_scheme['item-card-layout-css'])
        scroll_area.setWidgetResizable(True)
        content_widget = QWidget()
        grid_layout = QGridLayout(content_widget)  

        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(10)  

        column_factor = self.calculate_row_count()    
        card_size = self.width() // column_factor
        card_size = max(200, card_size)
        # Add cards to the grid layout
        for i, subject in enumerate(subjects):
            row = i // column_factor
            col = i % column_factor
            card = self.create_class_card(name=subject.class_name, size=card_size, item_icon_path=self.class_icon_path)
            grid_layout.addWidget(card, row, col)
                
        self.enable_delete_button(len(subjects) == 0)
        scroll_area.setWidget(content_widget)
        self.content_area_layout.addWidget(scroll_area)

    def enable_delete_button(self, is_enabled: bool):
        if is_enabled:
             self.delete_button.setVisible(True)
             self.delete_button.setIcon(self.delete_icon)
             self.delete_button.setStyleSheet(self.enabled_css)
             self.delete_button.setToolTip("This item will be deleted from your study!")
        else:
             self.delete_button.setVisible(False)
             self.delete_button.setIcon(self.disabled_delete_icon)
             self.delete_button.setStyleSheet(self.disbaled_css)
             self.delete_button.setToolTip("You cannot delete not empty item or analyzed document!")

    def calculate_row_count(self)-> int:
        column_factor = 3
        card_size = self.width() // column_factor
        while card_size > 200:
            column_factor += 1
            card_size = self.width() // column_factor
        column_factor -= 1 

        return column_factor

    def display_class(self, subject: StudyStreamSubject, on_save_item):
        self.on_save_item = on_save_item
        self.reset_content()
        if subject:
            self.study_class = subject
            self.title_button.setText(subject.class_name)
            self.title_button.setIcon(self.class_icon)

            fields_grid = QGridLayout()
            self.create_document_field(fields_grid, "Class Name:", subject.class_name, 0, 
                                       setter_lambda=lambda text: setattr(subject, 'class_name', text), is_read_only=False)
            self.create_datetime_field(fields_grid, "Start Date:", subject.start_date, 1, 
                                       lambda qdatetime: setattr(subject, 'start_date', qdatetime.toPython()), is_read_only=False)
            self.create_datetime_field(fields_grid, "Graduation Date:", subject.finish_date, 2, 
                                       lambda qdatetime: setattr(subject, 'finish_date', qdatetime.toPython()), is_read_only=False)
            self.content_area_layout.addLayout(fields_grid)
            self.add_document_card(documents=self.study_class.documents)
            self.enable_content()   
            self.update_content(is_enabled=True)   
            self.title_button.setDisabled(True) 

    def add_document_card(self, documents):
        scroll_area = QScrollArea()
        scroll_area.setStyleSheet(self.color_scheme['item-card-layout-css'])
        scroll_area.setWidgetResizable(True)
        content_widget = QWidget()
        grid_layout = QGridLayout(content_widget)  

        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(10)  
        
        column_factor = self.calculate_row_count()    
        card_size = self.width() // column_factor
        card_size = max(200, card_size)
        
        # Add cards to the grid layout
        for i, document in enumerate(documents):
            row = i // column_factor
            col = i % column_factor
            field_type = document.file_type_enum
            doc_icon_path = self.get_document_icon_path(file_type=field_type)
            card = self.create_class_card(name=document.name, size=card_size, item_icon_path=doc_icon_path)
            grid_layout.addWidget(card, row, col)
        
        self.enable_delete_button(len(documents) == 0)
        scroll_area.setWidget(content_widget)
        self.content_area_layout.addWidget(scroll_area)        

    def create_class_card(self, name, size: int, item_icon_path: str):
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setFixedSize(QSize(size, size)) 
        card.setStyleSheet(self.color_scheme['item-card-css'])
        
        card_layout = QVBoxLayout(card)  # Changed to QVBoxLayout to make the card content vertical
        icon_label = QLabel()
        pixmap = QPixmap(item_icon_path)
        icon_size = size / 4
        icon_label.setPixmap(pixmap.scaled(icon_size, icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))  # Adjusted icon size
        icon_label.setStyleSheet(self.color_scheme['item-card-icon-css'])
        
        name_label = HoverLabel(name)
        name_label.setStyleSheet(self.color_scheme['item-card-label-css'])
        name_label.setWordWrap(True)

        card_layout.addWidget(icon_label, alignment=Qt.AlignCenter)  # Center the icon
        card_layout.addWidget(name_label, alignment=Qt.AlignCenter)  # Center the name
        
        return card

    def display_document(self, document: StudyStreamDocument, on_save_item):
        self.on_save_item = on_save_item
        self.reset_content()
        if document:
            self.study_doc = document
            self.title_button.setText(document.name)
            self.title_button.setIcon(self.doc_icon)
            field_type = document.file_type_enum
            doc_icon = self.get_document_icon(file_type=field_type)
            fields_grid = QGridLayout()
            self.create_document_field(fields_grid, "File Name:", document.name, 0, 
                                       setter_lambda=lambda text: setattr(document, 'name', text), is_read_only=False, field_icon=doc_icon)
            self.create_document_field(fields_grid, "File Path:", document.file_path, 1, is_read_only=True)
            self.create_document_field(fields_grid, "Status:", document.status_enum.name, 2, is_read_only=True)
            self.create_datetime_field(fields_grid, "Created On:", document.creation_date, 3, is_read_only=True)
            self.create_datetime_field(fields_grid, "Processed On:", document.processed_date, 4, is_read_only=True)
            self.create_datetime_field(fields_grid, "Analyzed Since:", document.in_progress_date, 5, is_read_only=True)
            self.content_area_layout.addLayout(fields_grid)        
            self.enable_delete_button(document.status_enum == StudyStreamDocumentStatus.NEW)
            self.enable_content()

    def enable_content(self):
        self.title_button.setCheckable(True)
        self.title_button.setChecked(False)
        self.title_button.setDisabled(False)
        self.on_click()

    def reset_content(self):
        self.study_doc = None
        self.study_class = None
        self.study_school = None
        self.title_button.setText("No Document Selected")
        self.title_button.setIcon(self.default_icon)
        self.title_button.setCheckable(False)
        self.title_button.setChecked(False)
        self.title_button.setDisabled(True)
        self.clear_layout(self.content_area_layout)
        self.content_area.setVisible(False) 

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    self.clear_layout(child.layout())

    def create_document_field(self, layout, field_label, field_text, row, setter_lambda=None, is_read_only=False, field_icon=None):
        label = QLabel(field_label)
        label.setStyleSheet(self.label_css)    
        layout.addWidget(label, row, 0)
        if field_icon:            
            label.setPixmap(field_icon.pixmap(35, 35))  
        if field_text is None:
            field_text = "" 
        field_control = QLineEdit(field_text)
        field_control.setReadOnly(is_read_only)
        if is_read_only:
            field_control.setStyleSheet(self.readonly_control_css)
        else:   
            field_control.setStyleSheet(self.control_css)
            field_control.textChanged.connect(setter_lambda)
      
        layout.addWidget(field_control, row, 1)

        return field_control  
    
    def create_datetime_field(self, layout, field_label, datetime_value, row, setter_lambda=None, is_read_only=False):
        label = QLabel(field_label)
        label.setStyleSheet(self.label_css)    
        layout.addWidget(label, row, 0)
        datetime_field = QDateTimeEdit()
        if datetime_value:
            # Set the datetime value obtained from the database
            qdatetime_value = QDateTime(datetime_value.year, datetime_value.month, datetime_value.day,
                                    datetime_value.hour, datetime_value.minute, datetime_value.second)
            datetime_field.setDateTime(qdatetime_value)
        datetime_field.setDisabled(is_read_only)  
        if is_read_only:
            datetime_field.setStyleSheet(self.readonly_datetime_css)
        else:   
            datetime_field.setStyleSheet(self.datetime_css) 
            datetime_field.dateTimeChanged.connect(lambda qdatetime: setter_lambda(qdatetime.toPython() if qdatetime is not None else None))
    
        datetime_field.setDisplayFormat("yyyy-MM-dd HH:mm")
        layout.addWidget(datetime_field, row, 1) 

        return datetime_field

    def get_document_icon(self, file_type: FileType)-> QIcon:
        return QIcon(self.get_document_icon_path(file_type)) 
    
    def get_document_icon_path(self, file_type: FileType)-> str:
        if file_type == FileType.PDF:
            file_name = '/assets/pdf_icon_128.png'
        elif file_type == FileType.HTML:
            file_name = '/assets/html_icon_128.png'
        elif file_type == FileType.TEXT:
            file_name = '/assets/txt_icon_128.png'
        elif file_type == FileType.JS:
            file_name = '/assets/js_icon_128.png'
        elif file_type == FileType.DDL:
            file_name = '/assets/sql_icon_128.png'
        elif file_type == FileType.CSV:
            file_name = '/assets/csv_icon_128.png'
        elif file_type == FileType.JAVA:
            file_name = '/assets/java_icon_128.png'
        else:
            file_name = '/assets/doc_icon_128.png'
        return self.current_dir + file_name
    
    def get_school_type(self, school_type: StudyStreamSchoolType)-> QIcon:
        if school_type == StudyStreamSchoolType.HIGH_SCHOOL:
            return self.high_school_icon
        elif school_type == StudyStreamSchoolType.COLLEGE:
            return self.college_icon
        elif school_type == StudyStreamSchoolType.UNIVERSITY:
            return self.university_icon
        else:
            return self.course_icon
            
    def process_document(self):    
        if self.study_doc and self.study_doc.status_enum == StudyStreamDocumentStatus.NEW:
            # Asynchroneously run the adding Documemt to the embedding vector store 
            self.rotate_icon_angle = 0
            self.study_doc.status_enum = StudyStreamDocumentStatus.IN_PROGRESS
            print(f"process_document: {self.study_doc.file_path}")
            updated_doc = update_document(updated_document=self.study_doc)
            if updated_doc:   
                self.study_doc = updated_doc         
                self.rotate_icon() 
                self.timer = QTimer()
                self.timer.timeout.connect(self.rotate_icon)
                self.timer.start(500)
                self.document_in_progress = updated_doc
                self.async_task(document=self.document_in_progress) 
                if self.on_save_item:
                    self.on_save_item(name=updated_doc.name, status=updated_doc.status_enum)       
        else:
            self.logging.error(f"Document '{self.study_doc}' has the state is not acceptable for the analysis !!!")
    
    def async_task(self, document: StudyStreamDocument):   
        self.file_task = StudyStreamTaskWorker(add_file_content_to_db, self.db, self.document_splitter, document.file_path)
        self.file_task.finished.connect(lambda result: self.on_task_complete(result))
        self.file_task.error.connect(lambda error: self.on_task_error(error))
        self.file_task.run()

    def on_task_complete(self, result):
        if self.document_in_progress:
            self.logging.info(f"Has finished processing '{self.document_in_progress.name}': {result}")
            self.document_in_progress.status_enum = StudyStreamDocumentStatus.PROCESSED
            self.update_document_on_finished_load(updated_document=self.document_in_progress)              

    def on_task_error(self, error):
        if self.file_in_progress:
            item_target = self.file_in_progress.data(0, Qt.ItemDataRole.UserRole)
            if isinstance(item_target, StudyStreamDocument):
                self.logging.info(f"Failed to rocess '{item_target.name}': {error}")
                self.document_in_progress.status_enum = StudyStreamDocumentStatus.NEW
                self.update_document_on_finished_load(updated_document=self.document_in_progress)  

    def update_document_on_finished_load(self, updated_document: StudyStreamDocument):
        if self.timer:
            self.timer.stop()
            self.timer = None  
        updated_doc = update_document(updated_document=self.document_in_progress)
        if self.study_doc and self.study_doc.id == updated_doc.id:
            self.study_doc = updated_doc
        self.document_in_progress = None                 
        self.on_click()    
        if self.on_save_item:
            self.on_save_item(name=updated_doc.name, status=updated_doc.status_enum)


    def rotate_icon(self):    
        new_icon, self.rotate_icon_angle = StudyStreamMessageType.rotate_icon(
            rotating_icon=self.rotating_icon, 
            rotate_icon_angle=self.rotate_icon_angle
        )
        self.llm_button.setIcon(new_icon)   
