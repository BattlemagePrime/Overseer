from PyQt6.QtWidgets import (
    QWidget, QLabel, QComboBox, QLineEdit, QPushButton, 
    QVBoxLayout, QHBoxLayout, QCheckBox, QGroupBox,
    QFormLayout, QFileDialog, QMessageBox, QSizePolicy, QRadioButton,
    QFrame, QSpacerItem
)
from PyQt6.QtGui import QIcon, QPalette, QBrush, QPixmap
from PyQt6.QtCore import Qt
from pathlib import Path
import json
import os

class overseerUI(QWidget):
    def __init__(self, config_path=None):
        super().__init__()
        self.config_path = str(config_path) if config_path else str(Path(__file__).parent.parent / "sample_config.json")
        self.config_data = None
        if self.config_path:
            try:
                with open(self.config_path, 'r') as f:
                    self.config_data = json.load(f)
            except Exception:
                self.config_data = None
        self.init_ui()
        self.load_preferences()

    def closeEvent(self, event):
        """Save preferences when window is closed"""
        self.save_preferences()
        event.accept()

    def init_ui(self):
        self.setWindowTitle("Overseer")
        self.setMinimumSize(450, 500)
        
        # Set window icon using absolute path
        icon_path = Path(__file__).parent.parent / "Images" / "kimdosi_icon.ico"
        if not icon_path.exists():
            icon_path = icon_path.with_name("Kimdosi_icon.png")  # Try PNG as fallback
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        main_layout = QVBoxLayout()  # Use vertical layout for single column
        main_layout.setSpacing(10)

        # Binary section at the top
        binary_section = self.create_binary_section()
        binary_section.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        main_layout.addWidget(binary_section)

        # Tools section below binary
        tools_section = self.create_tools_section()
        tools_section.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(tools_section)

        # Restore bottom buttons to horizontal layout at the bottom
        bottom_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Analysis")
        self.start_btn.clicked.connect(self.start_analysis)
        self.stop_btn = QPushButton("Stop Analysis")
        self.stop_btn.clicked.connect(self.stop_analysis)
        self.results_btn = QPushButton("Open Results")
        self.results_btn.clicked.connect(self.open_results)
        bottom_layout.addWidget(self.stop_btn)
        bottom_layout.addWidget(self.results_btn)
        bottom_layout.addWidget(self.start_btn)
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

        # Preconfigure fields from config if available
        if self.config_data:
            self.preconfigure_from_config()

    def create_binary_section(self):
        group = QGroupBox("Binary/Zip")
        form = QFormLayout()
        form.setSpacing(6)
        form.setContentsMargins(5, 5, 5, 5)

        # File selection row
        binary_widget = QWidget()
        binary_layout = QHBoxLayout(binary_widget)
        binary_layout.setContentsMargins(0, 0, 0, 0)
        self.binary_path = QLineEdit()
        self.binary_path.setReadOnly(True)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_malware)
        binary_layout.addWidget(self.binary_path)
        binary_layout.addWidget(browse_btn)

        # Password field
        self.zip_password = QLineEdit()
        self.zip_password.setPlaceholderText("Zip Password (if any)")

        # Run and Admin checkboxes in a horizontal layout
        run_admin_widget = QWidget()
        run_admin_layout = QHBoxLayout(run_admin_widget)
        run_admin_layout.setContentsMargins(0, 0, 0, 0)
        run_admin_layout.setSpacing(10)
        self.run_check = QCheckBox("Run")
        self.admin_check = QCheckBox("As Admin")
        run_admin_layout.addWidget(self.run_check)
        run_admin_layout.addWidget(self.admin_check)
        run_admin_layout.addStretch()

        # VM fields
        self.vmware_radio = QRadioButton("VMware")
        self.virtualbox_radio = QRadioButton("VirtualBox")
        self.vmware_radio.setChecked(True)
        vm_type_widget = QWidget()
        vm_type_layout = QHBoxLayout(vm_type_widget)
        vm_type_layout.setContentsMargins(0, 0, 0, 0)

        self.username = QLineEdit()
        self.username.setPlaceholderText("VM Username")
        self.password = QLineEdit()
        self.password.setPlaceholderText("VM Password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        form.addRow("File:", binary_widget)
        form.addRow("Password:", self.zip_password)
        form.addRow(run_admin_widget)
        form.addRow("VM Username:", self.username)
        form.addRow("VM Password:", self.password)

        group.setLayout(form)
        return group

    def toggle_vm_fields(self):
        enabled = self.admin_check.isChecked()
        self.vm_username.setEnabled(enabled)
        self.vm_password.setEnabled(enabled)

    def preconfigure_from_config(self):
        if not isinstance(self.config_data, dict):
            return
        # Pre-fill binary path
        binary = self.config_data.get('binary', {})
        if binary.get('path'):
            self.binary_path.setText(binary['path'])
        if binary.get('run'):
            self.run_check.setChecked(binary['run'])
        if binary.get('as_admin'):
            self.admin_check.setChecked(binary['as_admin'])
        if binary.get('password'):
            self.zip_password.setText(binary['password'])
        # Pre-fill VM fields
        vm = self.config_data.get('vm', {})
        if vm.get('username'):
            self.username.setText(vm['username'])
        if vm.get('password'):
            self.password.setText(vm['password'])

        if vm.get('binary_password'):
            self.zip_password.setText(vm['binary_password'])
        # Pre-fill static tools
        for name, checked in self.config_data.get('static_tools', {}).items():
            if name in self.static_tools:
                self.static_tools[name].setChecked(checked)
        # Pre-fill dynamic tools
        for name, checked in self.config_data.get('dynamic_tools', {}).items():
            if name in self.dynamic_tools:
                self.dynamic_tools[name].setChecked(checked)
        # Pre-fill procmon settings
        procmon = self.config_data.get('procmon_settings', {})
        if 'enabled' in procmon and 'Procmon' in self.dynamic_tools:
            self.dynamic_tools['Procmon'].setChecked(procmon['enabled'])
        if 'duration' in procmon and hasattr(self, 'procmon_duration'):
            self.procmon_duration.setText(str(procmon['duration']))
        if 'disable_timer' in procmon and hasattr(self, 'procmon_disable_timer'):
            self.procmon_disable_timer.setChecked(procmon['disable_timer'])

    def create_tools_section(self):
        group = QGroupBox("Tools")
        layout = QVBoxLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(5, 5, 5, 5)

        # Static Tools frame without transparency
        static_frame = QFrame()
        static_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        static_frame.setLineWidth(1)
        static_layout = QVBoxLayout(static_frame)
        static_layout.setSpacing(6)
        static_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create title widget with checkbox
        static_title = QWidget()
        static_title_layout = QHBoxLayout(static_title)
        static_title_layout.setContentsMargins(0, 0, 0, 0)
        static_title_layout.addWidget(QLabel("Static Analysis"))
        self.static_all = QCheckBox("Select All")
        static_title_layout.addStretch()
        static_title_layout.addWidget(self.static_all)
        
        # Add custom title widget and tools to layout
        static_layout.addWidget(static_title)
        
        self.static_all.stateChanged.connect(lambda state: self.toggle_all_tools(state, self.static_tools))
        self.static_tools = {
            "Capa": QCheckBox("Capa"),
            "Yara": QCheckBox("Yara"), 
            "Exiftool": QCheckBox("Exiftool"),
            "Detect-it-Easy": QCheckBox("Detect It Easy"),
            "Floss": QCheckBox("FLOSS"),
            "ResourceExtract": QCheckBox("Resource Extract")
        }
        
        for tool in self.static_tools.values():
            static_layout.addWidget(tool)

        layout.addWidget(static_frame, 1)  # 1 stretch factor
        layout.addItem(QSpacerItem(0, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        
        # Dynamic Tools frame without transparency
        dynamic_frame = QFrame()
        dynamic_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        dynamic_frame.setLineWidth(1)
        dynamic_layout = QVBoxLayout(dynamic_frame)
        dynamic_layout.setSpacing(6)
        dynamic_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create title widget with checkbox
        dynamic_title = QWidget()
        dynamic_title_layout = QHBoxLayout(dynamic_title)
        dynamic_title_layout.setContentsMargins(0, 0, 0, 0)
        dynamic_title_layout.addWidget(QLabel("Dynamic Analysis"))
        self.dynamic_all = QCheckBox("Select All")
        dynamic_title_layout.addStretch()
        dynamic_title_layout.addWidget(self.dynamic_all)
        
        # Add custom title widget to layout
        dynamic_layout.addWidget(dynamic_title)
        
        self.dynamic_all.stateChanged.connect(lambda state: self.toggle_all_tools(state, self.dynamic_tools))
        
        # Create a dict without Procmon as it will be handled separately
        self.dynamic_tools = {
            "Fakenet": QCheckBox("FakeNet-NG"),
            "ProcDump": QCheckBox("ProcDump"),
            "Autoclicker": QCheckBox("Auto Clicker"),
            "CaptureFiles": QCheckBox("Capture Dropped Files"),
            "Screenshots": QCheckBox("Take Screenshots"),
            "RandomizeNames": QCheckBox("Randomize File Names")
        }
        
        # Procmon with inline settings
        procmon_widget = QWidget()
        procmon_layout = QHBoxLayout(procmon_widget)
        procmon_layout.setContentsMargins(0, 0, 0, 0)
        procmon_layout.setSpacing(10)
        
        self.dynamic_tools["Procmon"] = QCheckBox("Process Monitor")
        procmon_layout.addWidget(self.dynamic_tools["Procmon"])
        
        duration_widget = QWidget()
        duration_layout = QHBoxLayout(duration_widget)
        duration_layout.setContentsMargins(0, 0, 0, 0)
        duration_layout.setSpacing(4)
        
        duration_layout.addWidget(QLabel("Duration:"))
        self.procmon_duration = QLineEdit()
        self.procmon_duration.setFixedWidth(60)
        self.procmon_duration.setText("60")
        duration_layout.addWidget(self.procmon_duration)
        
        self.procmon_disable_timer = QCheckBox("Disable Timer")
        self.procmon_disable_timer.stateChanged.connect(
            lambda: self.procmon_duration.setDisabled(self.procmon_disable_timer.isChecked())
        )
        
        procmon_layout.addWidget(duration_widget)
        procmon_layout.addWidget(self.procmon_disable_timer)
        procmon_layout.addStretch()
        
        dynamic_layout.addWidget(procmon_widget)
        
        # Add remaining dynamic tools
        for tool in self.dynamic_tools.values():
            if tool != self.dynamic_tools["Procmon"]:  # Skip Procmon as it's already added
                dynamic_layout.addWidget(tool)

        layout.addWidget(dynamic_frame, 1)  # 1 stretch factor
        layout.addItem(QSpacerItem(0, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
    

        group.setLayout(layout)
        return group

    def toggle_all_tools(self, state, tool_dict):
        for tool in tool_dict.values():
            tool.setChecked(state == 2)  # 2 represents Qt.Checked


    def browse_malware(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Binary/Zip File", "", "All Files (*.*)"
        )
        if file_path:
            # Convert to Path object before setting
            self.binary_path.setText(str(Path(file_path)))

    def show_message(self, title, message, icon=QMessageBox.Icon.Information):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(icon)
        # Make text selectable
        msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard)
        # Set a minimum width to better handle long messages
        msg.setMinimumWidth(400)
        return msg.exec()



    def start_analysis(self):
        """Start the analysis process by preparing tools and binary"""
        if not self.binary_path.text():
            self.show_message("Error", "Please select a binary/zip file to analyze", QMessageBox.Icon.Warning)
            return
        try:
            # Create configuration for the analysis
            analysis_config = {
                "static_tools": {name: cb.isChecked() 
                               for name, cb in self.static_tools.items()},
                "dynamic_tools": {name: cb.isChecked() 
                                for name, cb in self.dynamic_tools.items()},
                "procmon_settings": {
                    "enabled": self.dynamic_tools["Procmon"].isChecked(),
                    "duration": self.procmon_duration.text() if not self.procmon_disable_timer.isChecked() else "0",
                    "disable_timer": self.procmon_disable_timer.isChecked()
                },
                "binary": {
                    "path": self.binary_path.text(),
                    "run": self.run_check.isChecked(),
                    "as_admin": self.admin_check.isChecked()
                }
            }

            if self.vm.text():
                analysis_config["vm"] = {
                    "username": self.username.text(),
                    "password": self.password.text()
                }

            # After transfer is complete, initialize Overseer and start analysis
            root_dir = Path(__file__).parent.parent.parent
            config_path = root_dir / "Tool_Transfer" / "analysis_config.json"
            
            if config_path.exists():
                pass
            
            self.show_message("Success", "Analysis preparation complete and analysis started", QMessageBox.Icon.Information)
        except Exception as e:
            self.show_message("Error", f"Failed to prepare analysis: {str(e)}", QMessageBox.Icon.Critical)

    def stop_analysis(self):
        # TODO: Implement analysis stop
        pass

    def open_results(self):
        # TODO: Implement results viewing
        pass

    def save_preferences(self):
        """Update only the relevant fields in the config file, preserving the rest."""
        try:
            # Load the current config
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
            else:
                config = {}

            # Update static_tools
            if 'static_tools' not in config:
                config['static_tools'] = {}
            for name, cb in self.static_tools.items():
                config['static_tools'][name] = cb.isChecked()

            # Update dynamic_tools
            if 'dynamic_tools' not in config:
                config['dynamic_tools'] = {}
            for name, cb in self.dynamic_tools.items():
                config['dynamic_tools'][name] = cb.isChecked()

            # Update procmon_settings
            if 'procmon_settings' not in config:
                config['procmon_settings'] = {}
            config['procmon_settings']['enabled'] = self.dynamic_tools["Procmon"].isChecked()
            config['procmon_settings']['disable_timer'] = self.procmon_disable_timer.isChecked()
            config['procmon_settings']['duration'] = self.procmon_duration.text()

            # Update binary section
            if 'binary' not in config:
                config['binary'] = {}
            config['binary']['path'] = self.binary_path.text()
            config['binary']['run'] = self.run_check.isChecked()
            config['binary']['as_admin'] = self.admin_check.isChecked()

            # Update VM section if any VM field is filled
            if  self.username.text() or self.password.text():
                if 'vm' not in config:
                    config['vm'] = {}
                config['vm']['username'] = self.username.text()
                config['vm']['password'] = self.password.text()
                config['vm']['binary_password'] = self.zip_password.text()
  

            # Save config
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.show_message("Error", f"Failed to save preferences: {str(e)}", QMessageBox.Icon.Warning)

    def load_preferences(self):
        """Load UI preferences from config file (using the correct config path)"""
        if not os.path.exists(self.config_path):
            return
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                

            # Load run settings
            self.run_check.setChecked(config.get("run", False))
            self.admin_check.setChecked(config.get("as_admin", False))
            
            # Load Procmon settings
            self.dynamic_tools["Procmon"].setChecked(config.get("procmon_enabled", False))
            self.procmon_disable_timer.setChecked(config.get("procmon_disable_timer", False))
            self.procmon_duration.setText(config.get("procmon_duration", "60"))
            
            # Load static tools
            self.static_tools["Capa"].setChecked(config.get("tool_Capa", False))
            self.static_tools["Floss"].setChecked(config.get("tool_Floss", False))
            self.static_tools["Yara"].setChecked(config.get("tool_Yara", False))
            self.static_tools["Detect-it-Easy"].setChecked(config.get("tool_Detect-It-Easy", False))
            self.static_tools["ResourceExtract"].setChecked(config.get("tool_ResourceExtract", False))
            self.static_tools["Exiftool"].setChecked(config.get("tool_Exiftool", False))
            self.static_tools["Binwalk"].setChecked(config.get("tool_Binwalk", False))
            
            # Load dynamic tools
            self.dynamic_tools["Fakenet"].setChecked(config.get("tool_FakeNet", False))
            self.dynamic_tools["ProcDump"].setChecked(config.get("tool_ProcDump", False))
            self.dynamic_tools["Autoclicker"].setChecked(config.get("tool_Autoclicker", False))
            self.dynamic_tools["CaptureFiles"].setChecked(config.get("tool_Capture_Dropped_Files", False))
            self.dynamic_tools["RandomizeNames"].setChecked(config.get("randomize_names", False))
            self.dynamic_tools["Screenshots"].setChecked(config.get("tool_Screenshots", False))
            
        except Exception as e:
            self.show_message("Error", f"Failed to load preferences: {str(e)}", QMessageBox.Icon.Warning)
