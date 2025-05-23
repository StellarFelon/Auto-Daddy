"""
Gemini Text Generator Module for Auto Daddy

This module handles text generation for ASMR daddy content using Google's Gemini 2.5 API.
It includes functionality for script length customization and prompt engineering.
"""

import os
from google import genai
from google.genai import types

class GeminiTextGenerator:
    """Class for generating ASMR daddy scripts using Gemini 2.5 API."""
    
    def __init__(self, api_key=None):
        """
        Initialize the Gemini text generator.
        
        Args:
            api_key (str, optional): Google Gemini API key. If None, will try to get from environment.
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable or pass as parameter.")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.5-flash-preview"  # Using the Flash Preview model
    
    def generate_script(self, theme="comforting", length="medium", custom_prompt=None):
        """
        Generate an ASMR daddy script based on theme and desired length.
        
        Args:
            theme (str): Theme for the ASMR content (e.g., "comforting", "sleep aid", "relaxation")
            length (str): Desired script length ("short", "medium", "long")
            custom_prompt (str, optional): Custom prompt to override the default prompt engineering
            
        Returns:
            str: Generated script with speaker annotations
        """
        # Map length to approximate word count
        length_map = {
            "short": 150,
            "medium": 300,
            "long": 600,
            "very long": 1000
        }
        
        word_count = length_map.get(length.lower(), 300)  # Default to medium if not specified
        
        # Create prompt for Gemini
        if custom_prompt:
            prompt = custom_prompt
        else:
            prompt = self._create_prompt(theme, word_count)
        
        # Generate content using Gemini
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)]
                )],
                generation_config=types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1024,
                    top_p=0.95,
                )
            )
            
            # Extract and format the generated script
            script = response.text
            return self._format_script(script)
            
        except Exception as e:
            return f"Error generating script: {str(e)}"
    
    def _create_prompt(self, theme, word_count):
        """
        Create a prompt for Gemini based on theme and word count.
        
        Args:
            theme (str): Theme for the ASMR content
            word_count (int): Target word count for the script
            
        Returns:
            str: Formatted prompt for Gemini
        """
        return f"""
        Create an ASMR daddy script with a warm, comforting tone on the theme of "{theme}".
        
        The script should be approximately {word_count} words long and formatted as a dialogue 
        with a single speaker (Speaker 1) who is the "daddy" character.
        
        Format the script with "Speaker 1:" prefix before each paragraph of dialogue.
        
        The tone should be gentle, reassuring, and caring - typical of ASMR "daddy" content.
        Include appropriate pauses indicated by "[pause]" and soft sounds like "[soft laugh]" 
        or "[gentle sigh]" where appropriate.
        
        Make sure the content is soothing, appropriate for relaxation, and follows a natural 
        conversational flow as if speaking directly to the listener.
        """
    
    def _format_script(self, raw_script):
        """
        Format the raw generated script to ensure proper speaker annotations.
        
        Args:
            raw_script (str): Raw script from Gemini
            
        Returns:
            str: Properly formatted script
        """
        # Ensure script has proper speaker annotations
        if "Speaker 1:" not in raw_script:
            # Add speaker annotation if missing
            lines = raw_script.split('\n')
            formatted_lines = []
            
            for line in lines:
                if line.strip():
                    if not line.startswith("Speaker 1:"):
                        formatted_lines.append(f"Speaker 1: {line}")
                    else:
                        formatted_lines.append(line)
                else:
                    formatted_lines.append(line)  # Keep empty lines
                    
            return '\n'.join(formatted_lines)
        
        return raw_script


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
    
    generator = GeminiTextGenerator(api_key)
    script = generator.generate_script(theme="bedtime relaxation", length="short")
    print(script)
