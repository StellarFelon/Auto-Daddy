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
    
    def generate_script(self, theme="comforting", length="medium", custom_prompt=None, speaker1_name="Speaker1", speaker2_name="Speaker2"):
        """
        Generate an ASMR script using the text generator for two speakers.
        
        Args:
            theme (str): Theme for the ASMR content
            length (str): Desired script length ("short", "medium", "long", "very long")
            custom_prompt (str, optional): Custom prompt to override default
            speaker1_name (str): Name for Speaker 1
            speaker2_name (str): Name for Speaker 2
            
        Returns:
            str: Generated script
        """
        self.current_script = self.text_generator.generate_script(
            theme=theme,
            length=length,
            custom_prompt=custom_prompt,
            speaker1_name=speaker1_name,
            speaker2_name=speaker2_name
        )
        return self.current_script
    
    def set_manual_script(self, script_text):
        """
        Set a manually created script.
        
        Args:
            script_text (str): The manually created script text.
                               Users should ensure it's formatted correctly for two speakers if intended.
            
        Returns:
            str: The script text as set.
        """
        # Removed automatic "Speaker 1:" prepending. 
        # Users providing manual scripts are responsible for their formatting.
        self.current_script = script_text
        return self.current_script
    
    def generate_audio(self, script=None, speaker1_name="Speaker1", speaker1_voice="Enceladus", speaker2_name="Speaker2", speaker2_voice="Puck", output_filename=None):
        """
        Generate audio from the current or provided script for two speakers.
        
        Args:
            script (str, optional): Script to use. If None, uses current_script.
            speaker1_name (str): Name/identifier for Speaker 1 in the script.
            speaker1_voice (str): Voice to use for Speaker 1.
            speaker2_name (str): Name/identifier for Speaker 2 in the script.
            speaker2_voice (str): Voice to use for Speaker 2.
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
            speaker1_name=speaker1_name,
            speaker1_voice=speaker1_voice,
            speaker2_name=speaker2_name,
            speaker2_voice=speaker2_voice
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

    # Define speaker names and voices for the test
    s1_name = "Gojo"
    s1_voice = "Enceladus"  # Assuming "Enceladus" is in available_voices
    s2_name = "Twink"
    s2_voice = "Puck"     # Assuming "Puck" is in available_voices
    
    # Test script generation for two speakers
    print(f"Generating two-speaker script for {s1_name} and {s2_name}...")
    script = auto_daddy.generate_script(
        theme="a tense confrontation", 
        length="medium",
        speaker1_name=s1_name,
        speaker2_name=s2_name
    )
    print(f"Script generated:\n{script}\n")
    
    # Test audio generation for two speakers
    if not script.startswith("Error"): # Proceed only if script generation was successful
        print(f"Generating two-speaker audio with voices {s1_voice} for {s1_name} and {s2_voice} for {s2_name}...")
        audio_path = auto_daddy.generate_audio(
            speaker1_name=s1_name,
            speaker1_voice=s1_voice,
            speaker2_name=s2_name,
            speaker2_voice=s2_voice
        )
        print(f"Audio generated: {audio_path}")
    else:
        print("Skipping audio generation due to script generation error.")
    
    # Test script saving
    script_path = auto_daddy.save_script()
    print(f"Script saved: {script_path}")
