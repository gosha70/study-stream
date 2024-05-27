# Copyright (c) EGOGE - All Rights Reserved.
# This software may be used and distributed according to the terms of the Apache-2.0 license.
import os
import shutil
import json
from PySide6.QtWidgets import (QVBoxLayout, QWidget, QDialog, 
                               QComboBox, QLineEdit, QPushButton,
                               QCheckBox, QLabel, QHBoxLayout, QGridLayout, QFrame)
from PySide6.QtGui import QIcon, Qt
from PySide6.QtCore import QSize
from dotenv import load_dotenv
from db.study_stream_dao import get_db_connection

# Define the path to the .env file
ENV_PATH = os.path.join(os.path.dirname(__file__), '..', 'profiles', '.env')

class StudyStreamSettings(QDialog):

    def __init__(self, parent, app_config, current_dir: str, logging):
        super().__init__(parent)
        self.current_dir = current_dir        
        self.load_color_scheme()
        self.app_config = app_config
        self.logging = logging
        self.initPanel()

    def load_color_scheme(self):
        self.env_color_mode = os.getenv("COLOR_SCHEME") 
        if self.env_color_mode == "light":
            color_scheme_name = "light-color-scheme"
        elif self.env_color_mode == "dark":
            color_scheme_name = "dark-color-scheme"
        else:
            color_scheme_name = "turquoise-color-scheme"
        with open(self.current_dir + '/color_schemes/' + color_scheme_name + '.json', 'r') as file:
            self.color_scheme = json.load(file) 
        self.main_color_scheme = self.color_scheme["settings-css"]   

    def get_color_scheme(self):
        return self.color_scheme

    def initPanel(self): 
        self.icon_css = self.main_color_scheme['icon-css']
        self.setWindowTitle("Study Stream Settings")
        self.setGeometry(100, 100, 600, 400)
        self.layout = QVBoxLayout(self)
        self.setStyleSheet(self.main_color_scheme['main-css'])

        self.button_css = self.main_color_scheme['button-css']
        self.button_hover_css = self.main_color_scheme['button-hover-css']
        self.button_pressed_css = self.main_color_scheme['button-pressed-css']

        self.control_css = self.main_color_scheme['control-css']        
        self.label_css = self.main_color_scheme['label-css']

        top_layout = QGridLayout()      
        
        llm_folder_label = QLabel("LLM Folder:")
        top_layout.addWidget(llm_folder_label, 0, 0)
        self.llm_folder_input = QLineEdit("NONE")
        self.llm_folder_input.setStyleSheet(self.control_css)
        top_layout.addWidget(self.llm_folder_input, 0, 1)

        self.checked_icon = QIcon(self.current_dir + self.app_config['checked_icon'])
        self.unchecked_icon = QIcon(self.current_dir + self.app_config['unchecked_icon'])
        self.open_ai_button = QPushButton("Open AI")
        self.open_ai_button_flag = False
        self.open_ai_button.setIcon(self.unchecked_icon)
        icon_width = 36 
        icon_height = 16 
        self.open_ai_button.setIconSize(QSize(icon_width, icon_height))
        self.open_ai_button.clicked.connect(self.check_open_ai)
        self.open_ai_button.setStyleSheet(self.icon_css)
        top_layout.addWidget(self.open_ai_button, 1, 0)

        open_ai_api_key_label = QLabel("Open AI API Key:")
        top_layout.addWidget(open_ai_api_key_label, 2, 0)
        self.open_ai_api_key_input = QLineEdit("NONE")
        self.open_ai_api_key_input.setEchoMode(QLineEdit.Password)
        self.open_ai_api_key_input.setStyleSheet(self.control_css)
        top_layout.addWidget(self.open_ai_api_key_input, 2, 1)

        self.show_password_flag = False
        self.lock_icon = QIcon(self.current_dir + self.app_config['lock-icon']) 
        self.unlock_icon = QIcon(self.current_dir + self.app_config['unlock-icon']) 
        self.show_password_button = QPushButton()
        self.show_password_button.setIcon(self.lock_icon)
        self.show_password_button.setIconSize(QSize(32, 32))  # Increased icon size
        self.show_password_button.setFixedSize(48, 48)
        self.show_password_button.setStyleSheet(self.icon_css)
        self.show_password_button.clicked.connect(self.toggle_password_visibility)
        top_layout.addWidget(self.show_password_button, 2, 2)

        self.color_scheme_label = QLabel("Color Scheme:")
        top_layout.addWidget(self.color_scheme_label, 3, 0)
        self.color_scheme_dropdown = QComboBox()
        self.color_scheme_dropdown.addItems(["dark", "light", "turquoise"])  
        self.color_scheme_dropdown.setStyleSheet(self.control_css)  
        top_layout.addWidget(self.color_scheme_dropdown, 3, 1)

        # Set column widths
        top_layout.setColumnStretch(0, 1)  # First column
        top_layout.setColumnStretch(1, 3)  # Second column (makes it wider)
        top_layout.setColumnStretch(2, 1)  # Third column
        top_layout.setColumnMinimumWidth(1, 200)  # Minimum width for the second column

        self.layout.addLayout(top_layout)
           
        # Add collapsible DB settings panel
        self.create_db_settings_panel()

        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("APPLY")
        self.apply_button.clicked.connect(self.apply_settings)              
        self.apply_button.setStyleSheet(f"""
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
        self.reset_button = QPushButton("RESET")        
        self.reset_button.setStyleSheet(f"""
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
        self.reset_button.clicked.connect(self.refresh_settings)
        self.cancel_button = QPushButton("CLOSE")
        self.cancel_button.setStyleSheet(f"""
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
        self.cancel_button.clicked.connect(self.close_settings)
        button_layout.addWidget(self.cancel_button, alignment=Qt.AlignmentFlag.AlignLeft)
        button_layout.addWidget(self.reset_button, alignment=Qt.AlignmentFlag.AlignCenter)
        button_layout.addWidget(self.apply_button, alignment=Qt.AlignmentFlag.AlignRight)
        self.layout.addLayout(button_layout)

    def check_open_ai(self):
        if self.open_ai_button_flag:
            self.open_ai_button_flag = False
            self.open_ai_button.setIcon(self.unchecked_icon) 
        else:
            self.open_ai_button_flag = True
            self.open_ai_button.setIcon(self.checked_icon)   
    
    def create_db_settings_panel(self):        
        db_settings = QWidget()
        db_settings.setStyleSheet(self.main_color_scheme['card-css'])

        self.toggle_layout = QVBoxLayout()
        self.toggle_layout.setSpacing(0)
        self.toggle_layout.setContentsMargins(0, 0, 0, 0)

        self.right_icon = QIcon(self.current_dir + self.app_config['right-arrow-icon']) 
        self.down_icon = QIcon(self.current_dir + self.app_config['down-arrow-icon']) 

        self.toggle_button = QPushButton("Database Settings")
        self.toggle_button.setIcon(self.right_icon)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)
        self.toggle_button.clicked.connect(self.on_toggle)
        self.toggle_layout.addWidget(self.toggle_button)

        self.content_area = QFrame()
        self.content_area.setStyleSheet(self.main_color_scheme['card-grid-css'])
        self.content_area.setVisible(False)
        self.toggle_layout.addWidget(self.content_area)

        db_settings.setLayout(self.toggle_layout)

        db_layout = QGridLayout()

        self.db_name = self.create_database_field(db_layout, "DB_NAME", "NONE", 0)
        self.db_user = self.create_database_field(db_layout, "DB_USER", "NONE", 1)
        self.db_psw = self.create_database_field(db_layout, "DB_PASSWORD", "NONE", 2)
        self.db_host = self.create_database_field(db_layout, "DB_HOST", "NONE", 3)
        self.db_port = self.create_database_field(db_layout, "DB_PORT", "NONE", 4)

        self.content_area.setLayout(db_layout)
        
        self.layout.addWidget(db_settings, alignment=Qt.AlignmentFlag.AlignTop)

    def create_database_field(self, layout, label_text, default_text, row):
        label = QLabel(label_text)
        label.setStyleSheet(self.label_css)
        layout.addWidget(label, row, 0)

        line_edit = QLineEdit(default_text)
        line_edit.setStyleSheet(self.control_css)
        layout.addWidget(line_edit, row, 1)

        return line_edit    

    def refresh_settings(self):  
        self.logging.info("Refesh Settings Dialog")
        self.orig_llm_folder = os.getenv("LLM_FOLDER")
        self.llm_folder_input.setText(self.orig_llm_folder)
        self.orig_open_ai_enabled = os.getenv("OPEN_AI_ENABLED", "false").lower() in ("true", "1", "t")
        self.open_ai_button_flag = not self.orig_open_ai_enabled
        self.check_open_ai()
        self.orig_api_key = os.getenv("OPEN_AI_KEY")
        self.open_ai_api_key_input.setText(self.orig_api_key)
        self.env_color_mode = os.getenv("COLOR_SCHEME") 
        if self.env_color_mode == "dark":
            self.color_scheme_dropdown.setCurrentIndex(0)
        elif self.env_color_mode == "light":
            self.color_scheme_dropdown.setCurrentIndex(1)
        else:
            self.color_scheme_dropdown.setCurrentIndex(2) 

        self.orig_db_name = os.getenv("DB_NAME")
        self.db_name.setText(self.orig_db_name)
        self.orig_db_user = os.getenv("DB_USER")  
        self.db_user.setText(self.orig_db_user)
        self.orig_db_psw = os.getenv("DB_PASSWORD")  
        self.db_psw.setText(self.orig_db_psw)
        self.orig_db_host = os.getenv("DB_HOST")  
        self.db_host.setText(self.orig_db_host)
        self.orig_db_port = os.getenv("DB_PORT")   
        self.db_port.setText(self.orig_db_port)

    def toggle_password_visibility(self):
        if self.show_password_flag:
            self.show_password_flag = False
            self.open_ai_api_key_input.setEchoMode(QLineEdit.Password)    
            self.show_password_button.setIcon(self.lock_icon)
        else:
            self.show_password_flag = True
            self.open_ai_api_key_input.setEchoMode(QLineEdit.Normal)
            self.show_password_button.setIcon(self.unlock_icon)

    def on_toggle(self):
        checked = self.toggle_button.isChecked()
        if checked:
            self.toggle_button.setIcon(self.down_icon)
        else:
            self.toggle_button.setIcon(self.right_icon)
        self.content_area.setVisible(checked)
        self.toggle_layout.activate()
        # Store the current width
        current_width = self.width()        
        # Adjust the size of the dialog based on its content
        self.adjustSize()        
        # Restore the width
        self.setFixedWidth(current_width)

    def close_settings(self):
        self.logging.info("Closing Settings Dialog")
        self.close()

    def apply_settings(self): 
        self.logging.info("Updating application settings ...")
        self.update_llm_folder()
        self.update_simple_properties()
        self.update_database()
        self.close()

    def update_database(self):
        new_db_name = self.db_name.text()
        new_db_user = self.db_user.text()
        new_db_password = self.db_psw.text()
        new_db_host = self.db_host.text()
        new_db_port = self.db_port.text()
        if new_db_name !=  self.orig_db_name or new_db_user != self.orig_db_user or new_db_password != self.orig_db_psw or new_db_host != self.orig_db_host or new_db_port != self.orig_db_port:
            # Check new database settings
            self.logging.info(f"Updating Database settings: (DB_NAME='{new_db_name}'; DB_USER='{new_db_user}'; DB_PASSWORD='{new_db_password}'; DB_HOST='{new_db_host}'; DB_PORT={new_db_port};")
            try:
                conn = get_db_connection(dbname=new_db_name, user=new_db_user, password=new_db_password, host=new_db_host, port=new_db_port)
                conn.close()
                self.update_env_var("DB_NAME", new_db_name)
                self.update_env_var("DB_USER", new_db_user)
                self.update_env_var("DB_PASSWORD", new_db_password)
                self.update_env_var("DB_HOST", new_db_host)
                self.update_env_var("DB_PORT", new_db_port)
                self.logging.info(f"New Database settings were applied.")
            except Exception as e:
                self.logging.error(f"Cannot connect to the database with the new settings: (DB_NAME='{new_db_name}'; DB_USER='{new_db_user}'; DB_PASSWORD='{new_db_password}'; DB_HOST='{new_db_host}'; DB_PORT={new_db_port};): {e}")

    def update_simple_properties(self):   
        new_open_ai_enabled = "true" if self.open_ai_button_flag else "false"        
        if self.orig_open_ai_enabled != new_open_ai_enabled:            
            self.update_env_var("OPEN_AI_ENABLED", new_open_ai_enabled)   
        new_text = self.open_ai_api_key_input.text()
        if self.orig_api_key != new_text:      
            self.update_env_var("OPEN_AI_KEY", new_text)
        new_text = self.color_scheme_dropdown.currentText()
        if self.env_color_mode != new_text:      
            self.update_env_var("COLOR_SCHEME", new_text)
            self.load_color_scheme()

    def update_llm_folder(self):
        """
        Copies all contents from the source directory to the destination directory.
        """
        dest_folder = self.llm_folder_input.text()
        if self.orig_llm_folder == dest_folder:
            return
        src_folder_path = self.current_dir + "/" + self.orig_llm_folder
        dest_folder_path = self.current_dir + "/" + dest_folder     
        # Ensure the destination directory exists
        if not os.path.exists(dest_folder_path):
            os.makedirs(dest_folder_path)
        if os.path.exists(src_folder_path):
            try:
                # Iterate over all files and directories in the source directory
                for item in os.listdir(src_folder_path):
                    s = os.path.join(src_folder_path, item)
                    d = os.path.join(dest_folder_path, item)
                    if os.path.isdir(s):
                        shutil.copytree(s, d, dirs_exist_ok=True)
                    else:
                        shutil.copy2(s, d)
                self.logging.info(f"Contents copied from {src_folder_path} to {dest_folder_path}")
                self.update_env_var("LLM_FOLDER", dest_folder)           
            except Exception as e:
                self.logging.error(f"An error occurred while copying contents of LLM folder from '{src_folder_path}' to '{dest_folder_path}': {e}")
    
    def update_env_var(self, key, value):
        # Read the .env file
        with open(ENV_PATH, 'r') as file:
            lines = file.readlines()

        # Update the .env file
        with open(ENV_PATH, 'w') as file:
            updated = False
            for line in lines:
                if line.startswith(f'{key}='):
                    print(f"UPDATE: {key} to {value}")
                    file.write(f'{key}={value}\n')
                    updated = True
                else:
                    file.write(line)
            
            # If the key was not found, add it to the end
            if not updated:
                print(f"NOT UPDATED: {key} to {value}")
                file.write(f'{key}={value}\n')    

    @staticmethod
    def load_profile(): 
        # Load the .env file
        load_dotenv(dotenv_path=ENV_PATH)    

    @staticmethod
    def is_env_found()-> bool: 
        return os.path.exists(ENV_PATH)       

    