# Copyright (c) EGOGE - All Rights Reserved.
# This software may be used and distributed according to the terms of the Apache-2.0 license.
import fitz  # PyMuPDF
from PyQt5.QtCore import QObject, Qt, QTimer, QVariant
from PyQt5.QtWidgets import (QDockWidget, QFileDialog, QToolBar, QAction, QWidget,
                             QTreeWidget, QTreeWidgetItem, QMenu, QVBoxLayout)
from PyQt5.QtGui import QIcon, QPixmap, QTransform

from langchain_community.vectorstores import Chroma
from embeddings.unstructured.document_splitter import DocumentSplitter
from embeddings.embedding_database import add_file_content_to_db

from .study_task import TaskWorker
from .study_document_view import StudyDocumentView
from study_stream_api.study_stream_subject import StudyStreamSubject
from study_stream_api.study_stream_document import StudyStreamDocument, DocumentStatus
from embeddings.unstructured.file_type import FileType

DEFAULT_FOLDER_NAME = 'New Subject'

class StudySubjectPanel(QDockWidget):
    def __init__(self, parent: QObject, document_view: StudyDocumentView, app_config, color_scheme, asserts_path: str, db: Chroma, logging):
        super().__init__(parent=parent)
        self.parent = parent
        self.document_view = document_view
        self.logging = logging
        self.asserts_path = asserts_path
        self.color_scheme = color_scheme
        self.app_config = app_config
        self.db = db
        self.document_splitter = DocumentSplitter(logging)
        self.page_index = 0  # Initialize page_index here
        self.selected_folder = None
        self.selected_file = None
        self.file_in_progress = None 
        self.file_task = None
        self.initPanel()

    def get_image_path(self, image_key: str)-> str:
        return self.asserts_path + self.app_config[image_key]
    
    def initPanel(self): 
        # Init icons and images
        self.folder_icon = QIcon(self.get_image_path("folder_icon"))
        self.folder_selected_icon = QIcon(self.get_image_path("opened_folder_icon")) 
        self.inactive_file_icon = QIcon(self.get_image_path("inactive_file_icon"))
        self.active_file_icon = QIcon(self.get_image_path("active_file_icon"))  
        self.loading_icon = QIcon(self.get_image_path("loading_icon"))          
        self.rotating_icon = QPixmap(self.get_image_path("loading_icon")) 

        self.setAllowedAreas(Qt.LeftDockWidgetArea)
        # Widget that holds the content of the dock
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Left Panel: Toolbar and List of PDFs
        toolbar = QToolBar("My Classes")
        # Setup the actions  app_config["file_attach_icon"])
        open_action = QAction(QIcon(self.get_image_path("new_doc_icon")), 'Load Document', self.parent)  # Use actual path to your icon
        open_action.triggered.connect(self.addDocument)
        toolbar.addAction(open_action)
        new_folder_action = QAction(QIcon(self.get_image_path("new_folder_icon")), 'New Class', self.parent)
        new_folder_action.triggered.connect(self.newClass)  # You need to define this method
        toolbar.addAction(new_folder_action)
        refresh_action = QAction(QIcon(self.get_image_path("refresh_icon")), 'Refresh', self.parent)
        refresh_action.triggered.connect(self.refresh)  # Currently a no-op
        toolbar.addAction(refresh_action)
        toggle_action = QAction(QIcon(self.get_image_path("toggle_in_icon")), 'Hide', self.parent)
        toggle_action.triggered.connect(self.togglePanel)  # You need to define this method
        toolbar.addAction(toggle_action)
        toolbar.setStyleSheet(self.color_scheme["toolbar-css"])            
        # Add the toolbar to the layout
        layout.addWidget(toolbar)    

        # Tree Widget for displaying folders and files
        self.class_tree = QTreeWidget()
        self.class_tree.setHeaderHidden(True)
        self.class_tree.setStyleSheet(self.color_scheme["main-css"])
        self.class_tree.itemSelectionChanged.connect(self.handleSelectionChanged)       
        self.class_tree.itemChanged.connect(self.onItemChanged) 
        self.class_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.class_tree.customContextMenuRequested.connect(self.onContextMenu) 
        self.class_tree.itemExpanded.connect(self.on_item_expanded)
        self.class_tree.itemCollapsed.connect(self.on_item_collapsed)
        layout.addWidget(self.class_tree)    

        # Set the main widget of the dock widget with the layout
        self.setWidget(widget)

    def togglePanel(self):
        # This method should handle the toggling of the panel's visibility or size
        pass

    def refresh(self):
        """Clear all selections in the tree widget."""
        self.selected_file = None
        self.selected_folder = None    
        self.class_tree.clearSelection()
        self.class_tree.setCurrentItem(None) 

    def on_item_expanded(self, item: QTreeWidgetItem):
        item_target = item.data(0, Qt.UserRole)
        if isinstance(item_target, StudyStreamSubject):
            item.setIcon(0, self.folder_selected_icon)
            if self.selected_folder is None:
                self.selected_folder = item

    def on_item_collapsed(self, item: QTreeWidgetItem):
        item_target = item.data(0, Qt.UserRole)
        if isinstance(item_target, StudyStreamSubject):
            item.setIcon(0, self.folder_icon)
            if item == self.selected_folder:
                self.selected_folder = None

    def onItemChanged(self, item: QTreeWidgetItem, column):
        if item.text(column).strip() == '':
            item.setText(column, DEFAULT_FOLDER_NAME)  # Provide a default name if empty
            item_target = item.data(0, Qt.UserRole)
            if isinstance(item_target, StudyStreamSubject):
                item_target.class_name = DEFAULT_FOLDER_NAME

    def onContextMenu(self, point):
        item = self.class_tree.itemAt(point)
        if isinstance(item, QTreeWidgetItem):
            self.class_tree.setCurrentItem(item)
            menu = QMenu()
            item_target = item.data(0, Qt.UserRole)
            if isinstance(item_target, StudyStreamDocument) and self.file_in_progress is None:   
                load_action = menu.addAction("Load")
            else:    
                load_action = None
            rename_action = menu.addAction("Rename")
            delete_action = menu.addAction("Delete")

            action = menu.exec_(self.class_tree.viewport().mapToGlobal(point))
            if action == rename_action:
                self.handlEdit(item)   
            elif action == delete_action:
                self.handleDelete(item)   
            elif load_action and action == load_action:     
                self.processDocument(item)       

    def handleDelete(self, item: QTreeWidgetItem):
        parent = item.parent()
        if parent:
            parent.removeChild(item)
        else:
            index = self.class_tree.indexOfTopLevelItem(item)
            self.class_tree.takeTopLevelItem(index)
    
    def handlEdit(self, item: QTreeWidgetItem):
        if item.flags() & Qt.ItemIsEditable:
            new_name = item.text(0)
            item_target = item.data(0, Qt.UserRole)
            if isinstance(item_target, StudyStreamDocument):
                item_target.name = new_name
            elif isinstance(item_target, StudyStreamSubject):
                item_target.class_name = new_name
                    
            self.class_tree.editItem(item, 0)  # Only edit if the item is set to be editable

    def processDocument(self, item: QTreeWidgetItem):    
        # Setup timer for icon animation
        item_target = item.data(0, Qt.UserRole)
        if isinstance(item_target, StudyStreamDocument):
            if item_target.file_path:
                # Asynchroneously run the adding Documemt to the embedding vector store 
                self.rotate_icon_angle = 0
                self.file_in_progress = item 
                item_target.status = DocumentStatus.IN_PROGRESS
                self.rotate_icon() 
                self.async_task(document=item_target)
                self.timer = QTimer()
                self.timer.timeout.connect(self.rotate_icon)
                self.timer.start(500)
    
    def async_task(self, document: StudyStreamDocument):   
        self.file_task = TaskWorker(add_file_content_to_db, self.db, self.document_splitter, document.file_path)
        self.file_task.finished.connect(lambda result: self.on_task_complete(result))
        self.file_task.error.connect(lambda error: self.on_task_error(error))
        self.file_task.run()

    def on_task_complete(self, result):
        if self.file_in_progress:
            item_target = self.file_in_progress.data(0, Qt.UserRole)
            if isinstance(item_target, StudyStreamDocument):
                self.logging.info(f"Has finished processing '{item_target.name}': {result}")
                if self.timer:
                    self.timer.stop()
                    self.timer = None            
                item_target.status = DocumentStatus.PROCESSED   
                self.file_in_progress.setIcon(0, self.active_file_icon) 
                self.file_in_progress = None    

    def on_task_error(self, error):
        if self.file_in_progress:
            item_target = self.file_in_progress.data(0, Qt.UserRole)
            if isinstance(item_target, StudyStreamDocument):
                self.logging.info(f"Failed to rocess '{item_target.name}': {error}")
                if self.timer:
                    self.timer.stop()
                    self.timer = None                        
                item_target.status = DocumentStatus.NEW       
                self.file_in_progress.setIcon(0, self.inactive_file_icon) 
                self.file_in_progress = None        

    def rotate_icon(self):    
        self.rotate_icon_angle += 10
        if self.rotate_icon_angle > 360:
            self.rotate_icon_angle = 0        
        transform = QTransform().rotate(self.rotate_icon_angle)
        rotated_pixmap = self.rotating_icon.transformed(transform, mode=Qt.FastTransformation)
        final_icon = QIcon(rotated_pixmap)
        self.file_in_progress.setIcon(0, final_icon) 

    def newClass(self):
        selected_item = self.class_tree.currentItem()
        if selected_item:
            item_target = selected_item.data(0, Qt.UserRole)
            if isinstance(item_target, StudyStreamDocument):
                selected_item = None
        new_class = QTreeWidgetItem()
        new_class.setText(0, DEFAULT_FOLDER_NAME)
        new_class.setIcon(0, self.folder_icon) 
        new_class.setFlags(new_class.flags() | Qt.ItemIsEditable)  # Make the item editable         
        new_class.setData(0, Qt.UserRole, QVariant(StudyStreamSubject(class_name=DEFAULT_FOLDER_NAME)))
        if selected_item:
            selected_item.addChild(new_class)          
            self.class_tree.expandItem(selected_item)
        else:
            self.class_tree.addTopLevelItem(new_class)  
        self.selected_folder = new_class    
        self.class_tree.editItem(new_class, 0)  # Optional: start editing immediately after adding
        
    def addDocument(self):
        path, _ = QFileDialog.getOpenFileName(self.parent, "Open PDF", "", "PDF files (*.pdf);;All files (*)")
        if path:
            self.updatePDFList(file_path=path)

    def updatePDFList(self, file_path: str):
        display_name = file_path.split('/')[-1]
        selected_item = self.class_tree.currentItem()
        if selected_item:
            item_target = selected_item.data(0, Qt.UserRole)
            if isinstance(item_target, StudyStreamDocument):
                selected_item = self.selected_folder
        new_file = QTreeWidgetItem()
        new_file.setText(0, display_name)
        new_file.setIcon(0, self.inactive_file_icon) 
        study_document = StudyStreamDocument(
            name=display_name, 
            file_path=file_path, 
            file_type=FileType.PDF,
            status=DocumentStatus.NEW
        )
        self.document_view.show_content(item=study_document)            
        new_file.setData(0, Qt.UserRole, QVariant(study_document))
        if selected_item:
            selected_item.addChild(new_file)            
            self.class_tree.expandItem(selected_item)
        else:
            self.class_tree.addTopLevelItem(new_file)        
        self.selected_file = new_file        
    
    def handleSelectionChanged(self):
        current_item = self.class_tree.currentItem()
        if current_item:
            print(current_item.text(0))
            item_target = current_item.data(0, Qt.UserRole)
            if isinstance(item_target, StudyStreamDocument): 
                if self.selected_file == current_item:
                    self.selected_file = None
                else:                 
                    self.selected_file = current_item
                    self.document_view.show_content(item=current_item)         
            else:     
                if self.selected_folder == current_item:
                    self.selected_folder = None
                else:                 
                    self.selected_folder = current_item
            
