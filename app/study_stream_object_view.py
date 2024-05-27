# Copyright (c) EGOGE - All Rights Reserved.
# This software may be used and distributed according to the terms of the Apache-2.0 license.
from typing import List
from PySide6.QtWidgets import (QHBoxLayout,  QToolTip, QScrollArea, QPushButton, QGridLayout, QLineEdit, 
                               QWidget, QLabel, QFrame, QVBoxLayout, QDateTimeEdit)
from PySide6.QtGui import QIcon,QPixmap
from PySide6.QtCore import QObject, QSize, Qt
from PySide6.QtCore import QDateTime

from study_stream_api.study_stream_document import StudyStreamDocument
from study_stream_api.study_stream_school import StudyStreamSchool
from study_stream_api.study_stream_subject import StudyStreamSubject
from study_stream_api.study_stream_school_type import StudyStreamSchoolType
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
            logging):
        super().__init__(parent)
        self.parent = parent
        self.dependent_object = dependent_object
        self.current_dir = current_dir   
        self.app_config = app_config 
        self.color_scheme = color_scheme
        self.logging = logging
        self.study_doc = None
        self.study_class = None
        self.study_school = None
        self.initUI()

    def initUI(self):
        self.setStyleSheet(self.color_scheme['card-css'])   
        self.control_css = self.color_scheme['control-css']
        self.readonly_control_css = self.color_scheme['control-readonly-css']
        self.label_css = self.color_scheme['label-css']
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

        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.title_button = QPushButton()
        self.title_button.setCheckable(True)
        self.title_button.setChecked(False)
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

        self.button_css = self.color_scheme['button-css']
        self.button_hover_css = self.color_scheme['button-hover-css']
        self.button_pressed_css = self.color_scheme['button-pressed-css']

        button_layout = QHBoxLayout()
        self.save_button = QPushButton(" SAVE ")
        self.save_button.clicked.connect(self.save_action)    
        self.save_button.setVisible(False)          
        self.save_button.setStyleSheet(f"""
            QPushButton {{
                {self.button_css} 
            }}
            QPushButton:hover {{
                {self.button_hover_css}   
            }}
            QPushButton:pressed {{
                {self.button_pressed_css}
            }}
        """)
        self.delete_button = QPushButton("DELETE")        
        self.delete_button.setStyleSheet(f"""
            QPushButton {{
                {self.button_css} 
            }}
            QPushButton:hover {{
                {self.button_hover_css}   
            }}
            QPushButton:pressed {{
                {self.button_pressed_css}
            }}
        """)
        self.delete_button.clicked.connect(self.delete_action)
        self.delete_button.setVisible(False)
        button_layout.addWidget(self.delete_button, alignment=Qt.AlignmentFlag.AlignLeft)
        button_layout.addWidget(self.save_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.main_layout.addLayout(button_layout)

        self.setLayout(self.main_layout)    

    def save_action(self):
        pass    
    
    def delete_action(self):
        pass       

    def on_click(self):         
        checked = self.title_button.isChecked()
        print(f"on_click: {checked}")
        self.update_content(is_enabled=checked)

    def update_content(self, is_enabled: bool):   
        self.content_area.setVisible(is_enabled) 
        self.dependent_object.setVisible(not is_enabled)
        self.save_button.setVisible(is_enabled)    
        self.delete_button.setVisible(is_enabled)     

    def display_school(self, school: StudyStreamSchool):
        print(f"display_class")
        self.reset_content()
        if school:
            self.study_school = school
            self.title_button.setText(school.name)
            self.title_button.setIcon(self.class_icon)

            school_icon = self.get_school_type(school_type=school.school_type_enum)

            fields_grid = QGridLayout()
            self.create_document_field(fields_grid, "School Name:", school.name, 0, is_read_only=False, field_icon=school_icon)
            self.create_datetime_field(fields_grid, "Start Date:", school.start_date, 1, is_read_only=False)
            self.create_datetime_field(fields_grid, "Graduation Date:", school.finish_date, 2, is_read_only=False)
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
        
        scroll_area.setWidget(content_widget)
        self.content_area_layout.addWidget(scroll_area)

    def calculate_row_count(self)-> int:
        column_factor = 3
        card_size = self.width() // column_factor
        while card_size > 200:
            column_factor += 1
            card_size = self.width() // column_factor
        column_factor -= 1 

        return column_factor

    def display_class(self, subject: StudyStreamSubject):
        print(f"display_class")
        self.reset_content()
        if subject:
            self.study_class = subject
            self.title_button.setText(subject.class_name)
            self.title_button.setIcon(self.class_icon)

            fields_grid = QGridLayout()
            self.create_document_field(fields_grid, "Class Name:", subject.class_name, 0, is_read_only=False)
            self.create_datetime_field(fields_grid, "Start Date:", subject.start_date, 1, is_read_only=False)
            self.create_datetime_field(fields_grid, "Graduation Date:", subject.finish_date, 2, is_read_only=False)
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

    def display_document(self, document: StudyStreamDocument):
        print(f"display_document")
        self.reset_content()
        if document:
            self.study_doc = document
            self.title_button.setText(document.name)
            self.title_button.setIcon(self.doc_icon)
            field_type = document.file_type_enum
            doc_icon = self.get_document_icon(file_type=field_type)
            fields_grid = QGridLayout()
            self.create_document_field(fields_grid, "File Name:", document.name, 0, is_read_only=False, field_icon=doc_icon)
            self.create_document_field(fields_grid, "File Path:", document.file_path, 1, is_read_only=True)
            self.create_document_field(fields_grid, "Status:", document.status_enum.name, 2, is_read_only=True)
            self.create_datetime_field(fields_grid, "Created On:", document.creation_date, 3, is_read_only=True)
            self.create_datetime_field(fields_grid, "Processed On:", document.processed_date, 4, is_read_only=True)
            self.create_datetime_field(fields_grid, "Analyzed Since:", document.in_progress_date, 5, is_read_only=True)
            self.content_area_layout.addLayout(fields_grid)

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

        print(f"reset_content: False")
        self.content_area.setVisible(False) 

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    self.clear_layout(child.layout())

    def create_document_field(self, layout, field_label, field_text, row, is_read_only=False, field_icon=None):
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
        layout.addWidget(field_control, row, 1)

        return field_control  
    
    def create_datetime_field(self, layout, field_label, datetime_value, row, is_read_only=False):
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
