import fitz  # PyMuPDF
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import (QVBoxLayout, QFileDialog, QListWidget, QListWidgetItem,
                             QToolBar, QAction, QTreeWidget, QTreeWidgetItem)
from PyQt5.QtGui import QIcon

class CurriculumPanel(QVBoxLayout):
    def __init__(self, parent: QObject, app_config, color_scheme, asserts_path: str):
        super().__init__()
        self.parent = parent
        self.asserts_path = asserts_path
        self.color_scheme = color_scheme
        self.app_config = app_config
        self.doc = None
        self.pdf_files = []
        self.page_index = 0  # Initialize page_index here
        self.previous_selection = None
        self.initPanel()

    def get_image_path(self, image_key: str)-> str:
        return self.asserts_path + self.app_config[image_key]
    
    def initPanel(self):
        self.folder_icon = QIcon(self.get_image_path("closed_folder_icon"))
        self.folder_selected_icon = QIcon(self.get_image_path("opened_folder_icon"))  # Selected state icon
        self.file_icon = QIcon(self.get_image_path("unselected_file_icon"))
        self.file_selected_icon = QIcon(self.get_image_path("selected_file_icon"))  # Selected state icon

        # Left Panel: Toolbar and List of PDFs
        self.toolbar = QToolBar("My Classes")

        # Setup the actions  app_config["file_attach_icon"])
        open_action = QAction(QIcon(self.get_image_path("open_doc_icon")), 'Load Document', self.parent)  # Use actual path to your icon
        open_action.triggered.connect(self.loadDocument)
        self.toolbar.addAction(open_action)

        new_folder_action = QAction(QIcon(self.get_image_path("new_folder_icon")), 'New Class', self.parent)
        new_folder_action.triggered.connect(self.newClass)  # You need to define this method
        self.toolbar.addAction(new_folder_action)

        refresh_action = QAction(QIcon(self.get_image_path("refresh_icon")), 'Refresh', self.parent)
        refresh_action.triggered.connect(lambda: None)  # Currently a no-op
        self.toolbar.addAction(refresh_action)

        toggle_action = QAction(QIcon(self.get_image_path("toggle_in_icon")), 'Hide', self.parent)
        toggle_action.triggered.connect(self.togglePanel)  # You need to define this method
        self.toolbar.addAction(toggle_action)

        self.toolbar.setStyleSheet(self.color_scheme["toolbar-css"])        
        self.addWidget(self.toolbar)

        # Tree Widget for displaying folders and files
        self.class_tree = QTreeWidget()
        self.class_tree.setStyleSheet(self.color_scheme["main-css"])
        self.class_tree.itemSelectionChanged.connect(self.handleSelectionChanged)        
        self.addWidget(self.class_tree)

    def loadDocument(self):
        path, _ = QFileDialog.getOpenFileName(self.parent, "Open PDF", "", "PDF files (*.pdf);;All files (*)")
        if path:
            self.doc = fitz.open(path)
            self.pdf_files.append(path)
            self.updatePDFList(file_path=path)

    def togglePanel(self):
        # This method should handle the toggling of the panel's visibility or size
        pass

    def newClass(self):
        selected_item = self.class_tree.currentItem()
        new_class = QTreeWidgetItem()
        new_class.setText(0, 'New Class')
        new_class.setIcon(0, self.folder_icon) 
        if selected_item:
            selected_item.addChild(new_class)
        else:
            self.class_tree.addTopLevelItem(new_class)
        self.class_tree.expandItem(new_class)

    def updatePDFList(self, file_path: str):
        print(file_path)
        selected_item = self.class_tree.currentItem()
        new_file = QTreeWidgetItem()
        new_file.setText(0, file_path.split('/')[-1])
        new_file.setIcon(0, self.file_icon) 
        if selected_item:
            selected_item.addChild(new_file)
        else:
            self.class_tree.addTopLevelItem(new_file)
        self.class_tree.expandItem(new_file)
    
    def handleSelectionChanged(self):
        # Reset the previous selection's icon
        if self.previous_selection:
            print(self.previous_selection.text(0))
            if self.previous_selection.text(0) in self.pdf_files:
                self.previous_selection.setIcon(0, self.file_icon)
            else:
                self.previous_selection.setIcon(0, self.folder_icon)
        
        # Set the icon for the current selection
        current_item = self.class_tree.currentItem()
        if current_item:
            print(current_item.text(0))
            if current_item.text(0) in self.pdf_files:
                current_item.setIcon(0, self.file_selected_icon )
            else:
                current_item.setIcon(0, self.folder_selected_icon)
        
        self.previous_selection = current_item  # Update the previous selection
    
        
    # Remaining methods (showPage, nextPage, prevPage, sendMessage) stay the same
