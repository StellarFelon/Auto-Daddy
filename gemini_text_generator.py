"""
Gemini Text Generator Module for Auto Daddy

This module handles text generation for ASMR daddy content using Google's Gemini 2.5 API.
It includes functionality for script length customization and prompt engineering.
"""

import os
from google import genai
from google.genai import types
from google.api_core import exceptions as google_exceptions

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
        self.model = "gemini-2.5-flash-preview-05-20" # Updated model name
    
    def generate_script(self, theme="comforting", length="medium", custom_prompt=None, speaker1_name="Daddy", speaker2_name="Listener"):
        """
        Generate an ASMR script based on theme, desired length, and speaker names.
        
        Args:
            theme (str): Theme for the ASMR content
            length (str): Desired script length ("short", "medium", "long")
            custom_prompt (str, optional): Custom prompt to override default
            speaker1_name (str): Name of the first speaker
            speaker2_name (str): Name of the second speaker
            
        Returns:
            str: Generated script
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
            prompt = self._create_prompt(theme, word_count, speaker1_name, speaker2_name)
        
        # Generate content using Gemini
        try:
            contents_payload = [types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)]
            )]

            current_generate_content_config = types.GenerateContentConfig(
                response_mime_type="text/plain"
            )
            try:
                current_generate_content_config.thinking_config = types.ThinkingConfig(thinking_budget=0)
            except AttributeError:
                # If types.ThinkingConfig doesn't exist or cannot be set, proceed without it
                pass

            script_parts = []
            for chunk in self.client.models.generate_content_stream(
                model=self.model,
                contents=contents_payload,
                config=current_generate_content_config,
            ):
                if chunk.text: # Ensure text exists
                    script_parts.append(chunk.text)
            
            raw_script = "".join(script_parts)
            return self._format_script(raw_script) # Or just return raw_script

        except google_exceptions.InvalidArgument as e:
            return f"API Invalid Argument error generating script ({type(e).__name__}): {str(e)}"
        except google_exceptions.GoogleAPIError as e:
            return f"Google API Error generating script ({type(e).__name__}): {str(e)}"
        except Exception as e:
            return f"Unexpected error generating script ({type(e).__name__}): {str(e)}"
    
    def _create_prompt(self, theme, word_count, speaker1_name, speaker2_name):
        """
        Create a prompt for Gemini based on theme, word count, and speaker names.
        
        Args:
            theme (str): Theme for the ASMR content
            word_count (int): Target word count for the script
            speaker1_name (str): Name of the first speaker
            speaker2_name (str): Name of the second speaker
            
        Returns:
            str: Formatted prompt for Gemini
        """
        return f"""
        Create an ASMR script with a {theme} tone, approximately {word_count} words long.
        The script should be a dialogue between two speakers: {speaker1_name} and {speaker2_name}.
        Format the script with '{speaker1_name}:' and '{speaker2_name}:' prefixes before each respective line of dialogue.
        Include appropriate pauses like [pause] and soft sounds like [soft laugh] where suitable.
        The content should be soothing and appropriate for relaxation.
        Ensure a natural conversational flow.
        """
    
    def _format_script(self, raw_script):
        """
        Formats the raw generated script.
        For now, it returns the script as is, relying on prompt engineering for formatting.
        
        Args:
            raw_script (str): Raw script from Gemini
            
        Returns:
            str: Formatted script (currently, the raw script)
        """
        # Simplified: Return raw script, relying on prompt for formatting.
        # Future enhancements could add more robust formatting if needed.
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
    # Example for 2-speaker script
    script = generator.generate_script(
        theme="a friendly chat", 
        length="short", 
        speaker1_name="Alex", 
        speaker2_name="Jordan"
    )
    print(script)
