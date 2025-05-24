"""
Auto Daddy - PyQt UI Module

This module implements the desktop user interface for the Auto Daddy ASMR audio generation tool
using PyQt5.
"""

import os
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QTextEdit, QPushButton, QComboBox, 
                            QSlider, QFileDialog, QMessageBox, QGroupBox, QRadioButton,
                            QSpinBox, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

# Import Auto Daddy core functionality
from auto_daddy import AutoDaddy


class GenerateAudioThread(QThread):
    """Thread for generating audio without blocking the UI."""
    finished = pyqtSignal(str)
    progress = pyqtSignal(int)
    
    def __init__(self, auto_daddy, script, output_filename, speaker1_voice, speaker2_voice):
        super().__init__()
        self.auto_daddy = auto_daddy
        self.script = script
        self.output_filename = output_filename
        self.speaker1_voice = speaker1_voice
        self.speaker2_voice = speaker2_voice
    
    def run(self):
        # Simulate progress updates (since the actual API doesn't provide progress)
        for i in range(10):
            self.progress.emit(i * 10)
            self.msleep(200)  # Sleep for 200ms
            
        # Generate the audio
        result = self.auto_daddy.generate_audio(
            script=self.script,
            output_filename=self.output_filename,
            speaker1_voice=self.speaker1_voice,
            speaker2_voice=self.speaker2_voice
        )
        
        self.progress.emit(100)  # Complete the progress
        self.finished.emit(result)


class GenerateScriptThread(QThread):
    """Thread for generating script without blocking the UI."""
    finished = pyqtSignal(str)
    progress = pyqtSignal(int)
    
    def __init__(self, auto_daddy, theme, length, custom_prompt):
        super().__init__()
        self.auto_daddy = auto_daddy
        self.theme = theme
        self.length = length
        self.custom_prompt = custom_prompt
    
    def run(self):
        # Simulate progress updates (since the actual API doesn't provide progress)
        for i in range(10):
            self.progress.emit(i * 10)
            self.msleep(200)  # Sleep for 200ms
            
        # Generate the script
        result = self.auto_daddy.generate_script(
            theme=self.theme,
            length=self.length,
            custom_prompt=self.custom_prompt
        )
        
        self.progress.emit(100)  # Complete the progress
        self.finished.emit(result)


class AutoDaddyUI(QMainWindow):
    """Main window for the Auto Daddy application."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize Auto Daddy backend
        self.initialize_backend()
        
        # Set up the UI
        self.init_ui()
    
    def initialize_backend(self):
        """Initialize the Auto Daddy backend."""
        # Try to get API key from environment
        self.api_key = os.environ.get("GEMINI_API_KEY")
        
        # If no API key, prompt user
        if not self.api_key:
            self.api_key = self.prompt_for_api_key()
        
        # Set up output directory
        self.output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize Auto Daddy
        try:
            self.auto_daddy = AutoDaddy(api_key=self.api_key, output_dir=self.output_dir)
        except Exception as e:
            QMessageBox.critical(self, "Initialization Error", f"Failed to initialize Auto Daddy: {str(e)}")
            sys.exit(1)
    
    def prompt_for_api_key(self):
        """Prompt the user for a Gemini API key."""
        from PyQt5.QtWidgets import QInputDialog
        
        api_key, ok = QInputDialog.getText(
            self, 
            "API Key Required", 
            "Please enter your Google Gemini API key:",
            QLineEdit.Password
        )
        
        if ok and api_key:
            return api_key
        else:
            QMessageBox.critical(self, "API Key Required", "A valid API key is required to use Auto Daddy.")
            sys.exit(1)
    
    def init_ui(self):
        """Initialize the user interface."""
        # Set window properties
        self.setWindowTitle("Auto Daddy - ASMR Audio Generator")
        self.setGeometry(100, 100, 900, 700)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Add title and description
        title_label = QLabel("Auto Daddy")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        
        desc_label = QLabel("Generate ASMR daddy audio content with AI")
        desc_label.setFont(QFont("Arial", 12))
        desc_label.setAlignment(Qt.AlignCenter)
        
        main_layout.addWidget(title_label)
        main_layout.addWidget(desc_label)
        main_layout.addSpacing(20)
        
        # Create script generation section
        script_group = QGroupBox("Script Generation")
        script_layout = QVBoxLayout()
        
        # Script input method selection
        input_method_layout = QHBoxLayout()
        self.manual_radio = QRadioButton("Manual Script Input")
        self.ai_radio = QRadioButton("AI Script Generation")
        self.ai_radio.setChecked(True)  # Default to AI generation
        
        input_method_layout.addWidget(self.manual_radio)
        input_method_layout.addWidget(self.ai_radio)
        script_layout.addLayout(input_method_layout)
        
        # Connect radio buttons to toggle UI elements
        self.manual_radio.toggled.connect(self.toggle_script_input_method)
        self.ai_radio.toggled.connect(self.toggle_script_input_method)
        
        # AI generation options
        self.ai_options_widget = QWidget()
        ai_options_layout = QVBoxLayout(self.ai_options_widget)
        
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        self.theme_input = QLineEdit()
        self.theme_input.setPlaceholderText("e.g., bedtime relaxation, comfort after a long day")
        theme_layout.addWidget(self.theme_input)
        ai_options_layout.addLayout(theme_layout)
        
        length_layout = QHBoxLayout()
        length_layout.addWidget(QLabel("Script Length:"))
        self.length_combo = QComboBox()
        self.length_combo.addItems(["Short", "Medium", "Long", "Very Long"])
        self.length_combo.setCurrentIndex(1)  # Default to Medium
        length_layout.addWidget(self.length_combo)
        ai_options_layout.addLayout(length_layout)
        
        generate_btn_layout = QHBoxLayout()
        self.generate_script_btn = QPushButton("Generate Script")
        self.generate_script_btn.clicked.connect(self.generate_script)
        generate_btn_layout.addStretch()
        generate_btn_layout.addWidget(self.generate_script_btn)
        ai_options_layout.addLayout(generate_btn_layout)
        
        script_layout.addWidget(self.ai_options_widget)
        
        # Manual script input
        self.manual_input_widget = QWidget()
        self.manual_input_widget.setVisible(False)  # Hidden by default
        manual_input_layout = QVBoxLayout(self.manual_input_widget)
        manual_input_layout.addWidget(QLabel("Enter your script below:"))
        manual_input_layout.addWidget(QLabel("Use 'Speaker 1:' prefix for each paragraph (added automatically if missing)"))
        script_layout.addWidget(self.manual_input_widget)
        
        # Script text area (used for both manual input and displaying generated scripts)
        self.script_text = QTextEdit()
        self.script_text.setPlaceholderText("Your script will appear here. You can edit it before generating audio.")
        self.script_text.setMinimumHeight(200)
        script_layout.addWidget(self.script_text)
        
        # Script progress bar
        self.script_progress = QProgressBar()
        self.script_progress.setVisible(False)
        script_layout.addWidget(self.script_progress)
        
        script_group.setLayout(script_layout)
        main_layout.addWidget(script_group)
        
        # Create audio generation section
        audio_group = QGroupBox("Audio Generation")
        audio_layout = QVBoxLayout()
        
        # Voice selection
        voice_layout = QHBoxLayout()
        voice_layout.addWidget(QLabel("Voice:"))
        self.voice_combo = QComboBox()
        self.voice_combo.addItems(self.auto_daddy.get_available_voices())
        voice_layout.addWidget(self.voice_combo)
        audio_layout.addLayout(voice_layout)
        
        # Generate audio button
        audio_btn_layout = QHBoxLayout()
        self.generate_audio_btn = QPushButton("Generate Audio")
        self.generate_audio_btn.clicked.connect(self.generate_audio)
        audio_btn_layout.addStretch()
        audio_btn_layout.addWidget(self.generate_audio_btn)
        audio_layout.addLayout(audio_btn_layout)
        
        # Audio progress bar
        self.audio_progress = QProgressBar()
        self.audio_progress.setVisible(False)
        audio_layout.addWidget(self.audio_progress)
        
        # Audio output info
        self.audio_output_label = QLabel("Audio output will appear here")
        audio_layout.addWidget(self.audio_output_label)
        
        audio_group.setLayout(audio_layout)
        main_layout.addWidget(audio_group)
        
        # Create file management section
        file_group = QGroupBox("File Management")
        file_layout = QHBoxLayout()
        
        self.save_script_btn = QPushButton("Save Script")
        self.save_script_btn.clicked.connect(self.save_script)
        
        self.open_output_dir_btn = QPushButton("Open Output Folder")
        self.open_output_dir_btn.clicked.connect(self.open_output_dir)
        
        file_layout.addWidget(self.save_script_btn)
        file_layout.addWidget(self.open_output_dir_btn)
        
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def toggle_script_input_method(self):
        """Toggle between manual and AI script input methods."""
        self.ai_options_widget.setVisible(self.ai_radio.isChecked())
        self.manual_input_widget.setVisible(self.manual_radio.isChecked())
        
        if self.manual_radio.isChecked():
            self.script_text.clear()
            self.script_text.setPlaceholderText("Enter your script here...")
        else:
            self.script_text.clear()
            self.script_text.setPlaceholderText("Generated script will appear here...")
    
    def generate_script(self):
        """Generate a script using the AI."""
        if not self.ai_radio.isChecked():
            return
        
        theme = self.theme_input.text().strip()
        if not theme:
            QMessageBox.warning(self, "Input Required", "Please enter a theme for the script.")
            return
        
        length = self.length_combo.currentText().lower()
        
        # Show progress bar
        self.script_progress.setValue(0)
        self.script_progress.setVisible(True)
        self.generate_script_btn.setEnabled(False)
        self.statusBar().showMessage("Generating script...")
        
        # Generate script in a separate thread
        self.script_thread = GenerateScriptThread(
            self.auto_daddy,
            theme,
            length,
            None  # No custom prompt
        )
        self.script_thread.progress.connect(self.script_progress.setValue)
        self.script_thread.finished.connect(self.on_script_generated)
        self.script_thread.start()
    
    def on_script_generated(self, script):
        """Handle generated script."""
        self.script_text.setText(script)
        self.script_progress.setVisible(False)
        self.generate_script_btn.setEnabled(True)
        self.statusBar().showMessage("Script generated successfully")
    
    def generate_audio(self):
        """Generate audio from the current script."""
        script = self.script_text.toPlainText().strip()
        if not script:
            QMessageBox.warning(self, "Script Required", "Please generate or enter a script first.")
            return
        
        # If manual input, format the script
        if self.manual_radio.isChecked():
            script = self.auto_daddy.set_manual_script(script)
            self.script_text.setText(script)  # Update with formatted script
        
        selected_voice = self.voice_combo.currentText()
        
        # Show progress bar
        self.audio_progress.setValue(0)
        self.audio_progress.setVisible(True)
        self.generate_audio_btn.setEnabled(False)
        self.statusBar().showMessage("Generating audio...")
        
        # The AutoDaddy backend is designed for two speakers, each with a potentially different voice.
        # For simplicity in this UI version, we use the single selected voice 
        # for both speaker1_voice and speaker2_voice.
        # Generate audio in a separate thread
        self.audio_thread = GenerateAudioThread(
            self.auto_daddy,
            script,
            None,  # Use default filename
            speaker1_voice=selected_voice,
            speaker2_voice=selected_voice
        )
        self.audio_thread.progress.connect(self.audio_progress.setValue)
        self.audio_thread.finished.connect(self.on_audio_generated)
        self.audio_thread.start()
    
    def on_audio_generated(self, result):
        """Handle generated audio."""
        self.audio_progress.setVisible(False)
        self.generate_audio_btn.setEnabled(True)
        
        if result.startswith("Error"):
            QMessageBox.critical(self, "Audio Generation Error", result)
            self.statusBar().showMessage("Audio generation failed")
        else:
            self.audio_output_label.setText(f"Audio saved to: {result}")
            self.statusBar().showMessage("Audio generated successfully")
            
            # Ask if user wants to open the audio file
            reply = QMessageBox.question(
                self, 
                "Audio Generated", 
                f"Audio file saved to:\n{result}\n\nWould you like to open it?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                self.open_file(result)
    
    def save_script(self):
        """Save the current script to a file."""
        script = self.script_text.toPlainText().strip()
        if not script:
            QMessageBox.warning(self, "Empty Script", "There is no script to save.")
            return
        
        # Set the script in Auto Daddy
        if self.manual_radio.isChecked():
            self.auto_daddy.set_manual_script(script)
        else:
            self.auto_daddy.current_script = script
        
        # Save the script
        result = self.auto_daddy.save_script()
        
        if result.startswith("Error"):
            QMessageBox.critical(self, "Save Error", result)
        else:
            self.statusBar().showMessage(f"Script saved to: {result}")
            QMessageBox.information(self, "Script Saved", f"Script saved to:\n{result}")
    
    def open_output_dir(self):
        """Open the output directory in the file explorer."""
        import subprocess
        import platform
        
        try:
            if platform.system() == "Windows":
                os.startfile(self.output_dir)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", self.output_dir])
            else:  # Linux
                subprocess.call(["xdg-open", self.output_dir])
                
            self.statusBar().showMessage(f"Opened output directory: {self.output_dir}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open output directory: {str(e)}")
    
    def open_file(self, file_path):
        """Open a file with the default application."""
        import subprocess
        import platform
        
        try:
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", file_path])
            else:  # Linux
                subprocess.call(["xdg-open", file_path])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open file: {str(e)}")


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    window = AutoDaddyUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
