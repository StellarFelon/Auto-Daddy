"""
Auto Daddy - Integration Module

This module integrates the text generation and audio synthesis components
into a unified pipeline for the Auto Daddy ASMR audio generation tool.
"""

import os
import time
from datetime import datetime
from gemini_text_generator import GeminiTextGenerator
from audio_synthesizer import AudioSynthesizer


class AutoDaddy:
    """Main integration class for Auto Daddy ASMR audio generation tool."""
    
    def __init__(self, api_key=None, output_dir=None):
        """
        Initialize the Auto Daddy integration module.
        
        Args:
            api_key (str, optional): Google Gemini API key. If None, will try to get from environment.
            output_dir (str, optional): Directory to save output files. If None, uses current directory.
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable or pass as parameter.")
        
        # Set output directory
        self.output_dir = output_dir or os.path.join(os.getcwd(), "output")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize components
        self.text_generator = GeminiTextGenerator(api_key=self.api_key)
        self.audio_synthesizer = AudioSynthesizer(api_key=self.api_key)
        
        # Track current script and audio
        self.current_script = None
        self.current_audio_path = None
    
    def generate_script(self, theme="comforting", length="medium", custom_prompt=None):
        """
        Generate an ASMR daddy script using the text generator.
        
        Args:
            theme (str): Theme for the ASMR content
            length (str): Desired script length ("short", "medium", "long", "very long")
            custom_prompt (str, optional): Custom prompt to override default
            
        Returns:
            str: Generated script
        """
        self.current_script = self.text_generator.generate_script(
            theme=theme,
            length=length,
            custom_prompt=custom_prompt
        )
        return self.current_script
    
    def set_manual_script(self, script_text):
        """
        Set a manually created script.
        
        Args:
            script_text (str): The manually created script text
            
        Returns:
            str: Formatted script with proper speaker annotations
        """
        # Ensure script has proper speaker annotations
        if script_text and "Speaker 1:" not in script_text:
            lines = script_text.split('\n')
            formatted_lines = []
            
            for line in lines:
                if line.strip():
                    if not line.startswith("Speaker 1:"):
                        formatted_lines.append(f"Speaker 1: {line}")
                    else:
                        formatted_lines.append(line)
                else:
                    formatted_lines.append(line)  # Keep empty lines
                    
            self.current_script = '\n'.join(formatted_lines)
        else:
            self.current_script = script_text
            
        return self.current_script
    
    def generate_audio(self, script=None, voice=None, output_filename=None):
        """
        Generate audio from the current or provided script.
        
        Args:
            script (str, optional): Script to use. If None, uses current_script.
            voice (str, optional): Voice to use. If None, uses default.
            output_filename (str, optional): Custom filename. If None, generates one.
            
        Returns:
            str: Path to the generated audio file or error message
        """
        # Use provided script or current script
        script_to_use = script or self.current_script
        if not script_to_use:
            return "Error: No script available. Generate or set a script first."
        
        # Generate filename if not provided
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"asmr_daddy_{timestamp}.wav"
        
        # Ensure output path is absolute
        output_path = os.path.join(self.output_dir, output_filename)
        
        # Generate audio
        self.current_audio_path = self.audio_synthesizer.synthesize_audio(
            script=script_to_use,
            output_file=output_path,
            voice=voice
        )
        
        return self.current_audio_path
    
    def save_script(self, filename=None):
        """
        Save the current script to a text file.
        
        Args:
            filename (str, optional): Custom filename. If None, generates one.
            
        Returns:
            str: Path to the saved script file or error message
        """
        if not self.current_script:
            return "Error: No script available to save."
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"asmr_script_{timestamp}.txt"
        
        # Ensure output path is absolute
        output_path = os.path.join(self.output_dir, filename)
        
        try:
            with open(output_path, 'w') as f:
                f.write(self.current_script)
            return output_path
        except Exception as e:
            return f"Error saving script: {str(e)}"
    
    def get_available_voices(self):
        """
        Get list of available voices.
        
        Returns:
            list: List of available voice names
        """
        return self.audio_synthesizer.available_voices


# Example usage
if __name__ == "__main__":
    # For testing purposes
    import sys
    
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        print("Please provide a Gemini API key as argument or set GEMINI_API_KEY environment variable")
        sys.exit(1)
    
    # Create Auto Daddy instance
    auto_daddy = AutoDaddy(api_key=api_key)
    
    # Test script generation
    print("Generating script...")
    script = auto_daddy.generate_script(theme="bedtime relaxation", length="short")
    print(f"Script generated:\n{script}\n")
    
    # Test audio generation
    print("Generating audio...")
    audio_path = auto_daddy.generate_audio()
    print(f"Audio generated: {audio_path}")
    
    # Test script saving
    script_path = auto_daddy.save_script()
    print(f"Script saved: {script_path}")
