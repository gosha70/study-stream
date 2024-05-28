# Copyright (c) EGOGE - All Rights Reserved.
# This software may be used and distributed according to the terms of the Apache-2.0 license.
import os
import shutil
from typing import List

from PySide6.QtCore import QObject, Qt, QSize
from PySide6.QtWidgets import (QDockWidget, QFileDialog, QToolBar, QWidget, 
                             QTreeWidget, QTreeWidgetItem, QVBoxLayout, QMessageBox)
from PySide6.QtGui import QIcon, QPixmap, QAction

from .study_stream_document_view import StudyStreamDocumentView
from study_stream_api.study_stream_subject import StudyStreamSubject
from study_stream_api.study_stream_document import StudyStreamDocument
from study_stream_api.study_stream_document_status import StudyStreamDocumentStatus
from study_stream_api.study_stream_school import StudyStreamSchool
from study_stream_api.study_stream_school_type import StudyStreamSchoolType

from embeddings.unstructured.file_type import FileType
from db.study_stream_dao import fetch_all_schools_with_related_data, create_entity


DEFAULT_CLASS_NAME = 'My Class'
DEFAULT_SCHOOL_NAME = 'My School'

class StudyStreamDirectoryPanel(QDockWidget):
    def __init__(self, 
                 parent: QObject, 
                 document_view: StudyStreamDocumentView, 
                 app_config, 
                 color_scheme, 
                 asserts_path: str, 
                 logging):
        super().__init__(parent=parent)
        self.parent = parent
        self.document_view = document_view
        self.logging = logging
        self.object_view = document_view.get_object_view()
        self.asserts_path = asserts_path
        self.color_scheme = color_scheme
        self.app_config = app_config
        self.page_index = 0  # Initialize page_index here
        self.selected_folder = None
        self.selected_file = None
        self.selected_school = None
        self.schools = []
        self.displayed_target = None 
        self.initPanel()
        self.load_study_stream_schema()

    def get_image_path(self, image_key: str)-> str:
        return self.asserts_path + self.app_config[image_key]
    
    def initPanel(self): 
        # Init icons and images
        self.class_selected_icon = QIcon(self.get_image_path("opened_class_icon")) 
        self.class_icon = QIcon(self.get_image_path("class_icon")) 
        
        self.inactive_file_icon = QIcon(self.get_image_path("inactive_file_icon"))
        self.active_file_icon = QIcon(self.get_image_path("active_file_icon"))  
        self.loading_icon = QIcon(self.get_image_path("loading_icon"))   
        self.school_selected_icon = QIcon(self.get_image_path("opened_school_icon")) 
        self.school_icon = QPixmap(self.get_image_path("school_icon")) 

        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        # Widget that holds the content of the dock
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Left Panel: Toolbar and List of PDFs
        toolbar = QToolBar("My Study")
        button_size = self.color_scheme['button-icon-size']   
        toolbar.setIconSize(QSize(button_size, button_size))

        # Add a new school
        school_action = QAction(QIcon(self.get_image_path("new_school_icon")), 'New School', self.parent)
        school_action.triggered.connect(self.new_school)  
        toolbar.addAction(school_action)

        # Add a new class
        self.new_subject_action = QAction(QIcon(self.get_image_path("new_class_icon")), 'New Class', self.parent)
        self.new_subject_action.triggered.connect(self.new_class) 
        toolbar.addAction(self.new_subject_action)

        # Add a new document
        self.new_doc_action = QAction(QIcon(self.get_image_path("new_doc_icon")), 'New Document', self.parent)  # Use actual path to your icon
        self.new_doc_action.triggered.connect(self.import_document)
        toolbar.addAction(self.new_doc_action)

        # Add the refresh action
        refresh_action = QAction(QIcon(self.get_image_path("refresh_icon")), 'Refresh', self.parent)
        refresh_action.triggered.connect(self.refresh) 
        toolbar.addAction(refresh_action)
        
        toolbar.setStyleSheet(self.color_scheme["toolbar-css"])  
        layout.addWidget(toolbar)    

        # Tree Widget for displaying folders and files
        self.class_tree = QTreeWidget()
        self.class_tree.setHeaderHidden(True)
        self.class_tree.setStyleSheet(f"""
            QTreeWidget {{
                {self.color_scheme["main-css"]}                                 
            }}  
            QTreeWidget::item {{
                {self.color_scheme["main-css"]}    
            }}                                                  
            QTreeWidget::item:selected {{
                {self.color_scheme["selected-css"]}
            }}
            QTreeWidget::item:hover {{
                 {self.color_scheme["hover-css"]}
            }}
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {{
                border-image: none;
                image: url({self.asserts_path + self.app_config['right-arrow-icon']});
            }}
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {{
                border-image: none;
                image: url({self.asserts_path + self.app_config['down-arrow-icon']});
            }}            
        """)

        self.class_tree.itemSelectionChanged.connect(self.handle_selection_changed)       
        self.class_tree.itemChanged.connect(self.on_item_changed) 
        self.class_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.class_tree.itemExpanded.connect(self.on_item_expanded)
        self.class_tree.itemCollapsed.connect(self.on_item_collapsed)
        layout.addWidget(self.class_tree)    

        # Set the main widget of the dock widget with the layout
        self.setWidget(widget)

    def refresh(self):
        reply = QMessageBox.question(self, "Refresh Directory", "Please confirm if you want to refresh the study directory !", QMessageBox.Ok | QMessageBox.Cancel)
        if reply == QMessageBox.Ok:
            self.refresh_tree()

    def refresh_tree(self):        
        """Clear all selections in the tree widget."""
        self.selected_file = None
        self.selected_folder = None    
        self.selected_school = None  
        self.class_tree.clear()
        self.class_tree.clearSelection()
        self.class_tree.setCurrentItem(None) 
        self.load_study_stream_schema() 
    
    def on_save_item(self, entity):
        changed_item = self.find_item_with_id(entity=entity)
        if changed_item:
            if isinstance(entity, StudyStreamDocument): 
                changed_item.setText(0, entity.name)
                if entity.status_enum == StudyStreamDocumentStatus.IN_PROGRESS:
                    changed_item.setIcon(0, self.loading_icon)    
                elif entity.status_enum == StudyStreamDocumentStatus.PROCESSED:
                    changed_item.setIcon(0, self.active_file_icon) 
                else:   
                    changed_item.setIcon(0, self.inactive_file_icon) 
            elif isinstance(entity, StudyStreamSchool): 
                changed_item.setText(0, entity.name)
            elif isinstance(entity, StudyStreamSubject):  
                changed_item.setText(0, entity.class_name)                  

    def find_item_with_id(self, entity)-> QTreeWidgetItem:
        def search_item(item):
            # Retrieve the stored object from the item
            item_target = item.data(0, Qt.ItemDataRole.UserRole)
            if type(item_target) is type(entity) and item_target.id == entity.id:
                return item
            # Recursively search through the children
            for i in range(item.childCount()):
                result = search_item(item.child(i))
                if result:
                    return result
            return None

        # Iterate through the top-level items
        for i in range(self.class_tree.topLevelItemCount()):
            item = self.class_tree.topLevelItem(i)
            result = search_item(item)
            if result:
                return result
        return None                              

    def load_study_stream_schema(self)-> List[StudyStreamSchool]:
        self.schools = fetch_all_schools_with_related_data()
        for school in self.schools:
            school_node = self.add_school(school_entity=school)
            for subject in school.subjects:
                class_node = self.add_class(subject_entity=subject, parent_node=school_node, with_select=False)
                for document in subject.documents:
                    self.add_document(document_entity=document, parent_node=class_node, with_select=False)
        
        if self.schools and len(self.schools) > 0:
            self.selected_school = self.class_tree.topLevelItem(0)
            self.class_tree.setCurrentItem(self.selected_school)
            self.class_tree.expandItem(self.selected_school)   
            self.select_school(tree_item=self.selected_school, school=self.selected_school.data(0, Qt.ItemDataRole.UserRole))
        else:            
            self.selected_school = None
            self.selected_folder = None
            self.selected_file = None    

    def on_item_expanded(self, item: QTreeWidgetItem):
        item_target = item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(item_target, StudyStreamSubject):
            item.setIcon(0, self.class_selected_icon)
            if self.selected_folder is None:
                self.selected_folder = item

    def on_item_collapsed(self, item: QTreeWidgetItem):
        item_target = item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(item_target, StudyStreamSubject):
            item.setIcon(0, self.class_icon)
            if item == self.selected_folder:
                self.selected_folder = None

    def on_item_changed(self, item: QTreeWidgetItem, column):
        if item.text(column).strip() == '':
            item.setText(column, DEFAULT_CLASS_NAME)  # Provide a default name if empty
            item_target = item.data(0, Qt.ItemDataRole.UserRole)
            if isinstance(item_target, StudyStreamSubject):
                item_target.class_name = DEFAULT_CLASS_NAME
    
    def new_school(self):
        school_entity = StudyStreamSchool(school_name=DEFAULT_SCHOOL_NAME, school_type=StudyStreamSchoolType.COLLEGE) 
        school_entity = create_entity(school_entity)
        self.add_school(school_entity)

    def add_school(self, school_entity: StudyStreamSchool)-> QTreeWidgetItem:        
        school_node = QTreeWidgetItem()
        school_node.setChildIndicatorPolicy
        school_node.setText(0, school_entity.name)
        school_node.setIcon(0, self.school_icon) 
        school_node.setFlags(school_node.flags() | Qt.ItemFlag.ItemIsEditable)  # Make the item editable         
        school_node.setData(0, Qt.ItemDataRole.UserRole, school_entity)
        # School is always at the top level 
        self.class_tree.addTopLevelItem(school_node)  
        self.selected_school = school_node    
        self.class_tree.editItem(school_node, 0)  # Optional  
        #self.disable_editing(root=None, node=school_node)  

        return school_node

    def new_class(self):
        if self.selected_school is None:
            QMessageBox.warning(self, 'Blocked Creation', 'Does not support an orphan class, a school must be selected first !!!')  
            return
        subject_entity = StudyStreamSubject(class_name=DEFAULT_CLASS_NAME)
        school_entity = self.selected_school.data(0, Qt.ItemDataRole.UserRole)
        subject_entity.school_id = school_entity.id
        subject_entity = create_entity(subject_entity)

        self.add_class(subject_entity=subject_entity, parent_node=self.selected_school, with_select=True)

    def add_class(self, subject_entity: StudyStreamSubject, parent_node: QTreeWidgetItem, with_select: bool)-> QTreeWidgetItem:
        if parent_node is None:
            return  
        class_node = QTreeWidgetItem()
        class_node.setText(0, subject_entity.class_name)
        class_node.setIcon(0, self.class_icon) 
        class_node.setFlags(class_node.flags() | Qt.ItemFlag.ItemIsEditable)  # Make the item editable         
        class_node.setData(0, Qt.ItemDataRole.UserRole, subject_entity)
        parent_node.addChild(class_node)    
        #self.disable_editing(root=parent_node, node=class_node)  
        if with_select:  
            self.class_tree.expandItem(parent_node) 
            self.selected_folder = class_node    
            self.class_tree.editItem(class_node, 0) 

        return class_node    
    
    def import_document(self):
        if self.selected_folder is None:
            QMessageBox.warning(self, 'Blocked Creation', 'Does not support orphan documents, a class must be selected first !!!')
            return
        
        # Define file dialog filter for supported file types
        file_filter = "Supported files (*.csv *.ddl *.xlsx *.java *.js *.json *.html *.md *.pdf *.py *.rtf *.sql *.txt *.xml *.xsl *.yaml);;All files (*)"
        
        doc_path, _ = QFileDialog.getOpenFileName(self.parent, "Open File", "", file_filter)
        if doc_path:
            doc_name = doc_path.split('/')[-1]
            file_type_enum = FileType.from_str_by_extension(file_name=doc_name) 
            if file_type_enum is None:
                QMessageBox.warning(self, 'Unsupported File Type', 'The selected file type is not supported.')
                return
            
             # Define the document folder path
            document_folder = self.get_document_folder()
            
            # Create the document folder if it doesn't exist
            os.makedirs(document_folder, exist_ok=True)

            # Define the destination path
            destination_path = os.path.join(document_folder, doc_name)
            
            # Copy the file to the document folder
            shutil.copy(doc_path, destination_path)

            class_entity = self.selected_folder.data(0, Qt.ItemDataRole.UserRole)
            doc_entity = StudyStreamDocument(
                name=doc_name, 
                file_path=destination_path,  # Update the file path to the new location
                file_type_enum=file_type_enum,
                status_enum=StudyStreamDocumentStatus.NEW
            )
            doc_entity.subject_id = class_entity.id
            doc_entity = create_entity(doc_entity)
            self.add_document(document_entity=doc_entity, parent_node=self.selected_folder, with_select=True)

    def get_document_folder(self)-> str:
        return self.asserts_path + "/" + os.getenv("DOCUMENT_FOLDER") 

    def add_document(self, document_entity: StudyStreamDocument, parent_node: QTreeWidgetItem, with_select=False)-> QTreeWidgetItem: 
        if parent_node is None:      
            return   
        new_file = QTreeWidgetItem()
        new_file.setText(0, document_entity.name)
        if document_entity.status_enum == StudyStreamDocumentStatus.IN_PROGRESS:
            new_file.setIcon(0, self.loading_icon)    
        elif document_entity.status_enum == StudyStreamDocumentStatus.PROCESSED:
            new_file.setIcon(0, self.active_file_icon) 
        else:   
            new_file.setIcon(0, self.inactive_file_icon)   
        #self.document_view.show_content(item=document_entity)            
        new_file.setData(0, Qt.ItemDataRole.UserRole, document_entity)
        parent_node.addChild(new_file)   
        #self.disable_editing(root=parent_node, node=new_file)  
        if with_select is None:        
            self.class_tree.expandItem(parent_node)
            self.selected_file = new_file     

        return new_file   
        
    def disable_editing(self, root, node):
        if not root:
            root = self.class_tree.invisibleRootItem()
        node.setFlags(root.flags() & ~Qt.ItemIsEditable)
    
    def handle_selection_changed(self):
        current_item = self.class_tree.currentItem()
        if current_item:
            item_target = current_item.data(0, Qt.ItemDataRole.UserRole)
            if isinstance(item_target, StudyStreamDocument): 
                if item_target != self.displayed_target:                    
                    self.selected_file = current_item
                    self.document_view.show_content(item=current_item)    
                    self.new_subject_action.setEnabled(False)  
                    self.new_doc_action.setEnabled(False)   
                    self.displayed_target = item_target   
                    self.document_view.show_content(item=item_target)
                    self.object_view.display_document(document=item_target, on_save_item=self.on_save_item, on_delete_item=self.refresh_tree) 
            elif isinstance(item_target, StudyStreamSubject):     
                if item_target != self.displayed_target:      
                    self.selected_folder = current_item   
                    self.selected_school = None
                    self.selected_file = None  
                    self.new_subject_action.setEnabled(False)  
                    self.new_doc_action.setEnabled(True)    
                    self.displayed_target = item_target   
                    self.object_view.display_class(subject=item_target, on_save_item=self.on_save_item, on_delete_item=self.refresh_tree)  
            elif isinstance(item_target, StudyStreamSchool):     
                if item_target != self.displayed_target:   
                    self.select_school(tree_item=current_item, school=item_target)  
    
    def select_school(self, tree_item, school: StudyStreamSchool):
        self.selected_school = tree_item
        self.selected_folder = None
        self.selected_file = None
        self.new_subject_action.setEnabled(True)
        self.new_doc_action.setEnabled(False) 
        self.displayed_target = school 
        self.object_view.display_school(school=school, on_save_item=self.on_save_item, on_delete_item=self.refresh_tree) 