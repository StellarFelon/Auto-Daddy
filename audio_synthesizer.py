"""
Audio Synthesis Module for Auto Daddy

This module handles the conversion of text scripts to audio using Google's
multi-speaker API for ASMR daddy content.
"""

import base64
import mimetypes
import os
import re
import struct
from google import genai
from google.genai import types
from google.api_core import exceptions as google_exceptions


class AudioSynthesizer:
    """Class for synthesizing audio from ASMR daddy scripts using Google's multi-speaker API."""
    
    def __init__(self, api_key=None):
        """
        Initialize the audio synthesizer.
        
        Args:
            api_key (str, optional): Google Gemini API key. If None, will try to get from environment.
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable or pass as parameter.")
        
        self.client = genai.Client(api_key=self.api_key)
        
        # Default voice configurations
        self.default_voice = "Enceladus"  # Warm, comforting voice suitable for "daddy" ASMR
        self.available_voices = [
            "Zephyr",     # Bright
            "Puck",       # Upbeat
            "Charon",     # Informative
            "Kore",       # Firm
            "Fenrir",     # Excitable
            "Leda",       # Youthful
            "Orus",       # Firm
            "Aoede",      # Breezy
            "Callirhoe",  # Easy-going
            "Autonoe",    # Bright
            "Enceladus",  # Breathy
            "Iapetus",    # Clear
            "Umbriel",    # Easy-going
            "Algieba",    # Smooth
            "Despina",    # Smooth
            "Erinome",    # Clear
            "Algenib",    # Gravelly
            "Rasalgethi", # Informative
            "Laomedeia",  # Upbeat
            "Achernar",   # Soft
            "Alnilam",    # Firm
            "Schedar",    # Even
            "Gacrux",     # Mature
            "Pulcherrima",# Forward
            "Achird",     # Friendly
            "Zubenelgenubi",# Casual
            "Vindemiatrix",# Gentle
            "Sadachbia",  # Lively
            "Sadaltager", # Knowledgeable
            "Sulafar"     # Warm
        ]
    
    def synthesize_audio(self, script, output_file, model_name, speaker1_name="Speaker1", speaker1_voice="Enceladus", speaker2_name="Speaker2", speaker2_voice="Puck", instructive_prefix="Read aloud in a natural, engaging tone, following the speaker cues and any emotional or contextual notes provided in the script:\n\n"):
        """
        Synthesize audio from the provided script for two speakers.
        
        Args:
            script (str): The script text with speaker annotations (e.g., "Speaker1:", "Speaker2:")
            output_file (str): Path to save the output audio file
            model_name (str): Name of the TTS model to use, like 'gemini-2.5-pro-preview-tts' or 'gemini-2.5-flash-preview-tts'.
            speaker1_name (str): Name/identifier for Speaker 1 in the script
            speaker1_voice (str): Voice to use for Speaker 1
            speaker2_name (str): Name/identifier for Speaker 2 in the script
            speaker2_voice (str): Voice to use for Speaker 2
            instructive_prefix (str): Text to prepend to the script to guide TTS model tone.
            
        Returns:
            str: Path to the saved audio file or error message
        """
        if not script:
            return "Error: Empty script provided"
        
        # Ensure speaker1_voice and speaker2_voice are valid, or use defaults
        s1_voice = speaker1_voice if speaker1_voice in self.available_voices else self.default_voice
        s2_voice = speaker2_voice if speaker2_voice in self.available_voices else self.default_voice # Or a different default like Puck
        if speaker2_voice not in self.available_voices and self.default_voice == s2_voice : # ensure different default if s1 also defaulted
             available_defaults = [v for v in self.available_voices if v != s1_voice]
             s2_voice = available_defaults[0] if available_defaults else s1_voice # fallback to s1_voice if no other default

        try:
            # Configure the speech generation for multi-speaker
            generate_content_config = types.GenerateContentConfig(
                temperature=1, 
                response_modalities=["audio"],
                speech_config=types.SpeechConfig(
                    multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                        speaker_voice_configs=[
                            types.SpeakerVoiceConfig(
                                speaker=speaker1_name,
                                voice_config=types.VoiceConfig(
                                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                        voice_name=s1_voice
                                    )
                                ),
                            ),
                            types.SpeakerVoiceConfig(
                                speaker=speaker2_name,
                                voice_config=types.VoiceConfig(
                                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                        voice_name=s2_voice
                                    )
                                ),
                            ),
                        ]
                    ),
                ),
            )
            
            # Prepare the content for generation
            # Prepend an instructive phrase to guide the TTS model's tone and adherence to script cues.
            prefixed_script = instructive_prefix + script
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=prefixed_script),
                    ],
                ),
            ]
            
            # Generate the audio content
            audio_data = None
            for chunk in self.client.models.generate_content_stream(
                model=model_name,
                contents=contents,
                config=generate_content_config,
            ):
                if (
                    chunk.candidates is None
                    or chunk.candidates[0].content is None
                    or chunk.candidates[0].content.parts is None
                ):
                    continue
                
                if chunk.candidates[0].content.parts[0].inline_data:
                    inline_data = chunk.candidates[0].content.parts[0].inline_data
                    data_buffer = inline_data.data
                    file_extension = mimetypes.guess_extension(inline_data.mime_type)
                    
                    if file_extension is None:
                        file_extension = ".wav"
                        data_buffer = self._convert_to_wav(inline_data.data, inline_data.mime_type)
                    
                    # Ensure output file has correct extension
                    if not output_file.endswith(file_extension):
                        output_file = f"{os.path.splitext(output_file)[0]}{file_extension}"
                    
                    # Save the audio data
                    self._save_binary_file(output_file, data_buffer)
                    audio_data = data_buffer
                    break
            
            if audio_data:
                return output_file
            else:
                return "Error: No audio data generated"

        except google_exceptions.InvalidArgument as e:
            return f"API Invalid Argument error synthesizing audio ({type(e).__name__}): {str(e)}"
        except google_exceptions.GoogleAPIError as e:
            return f"Google API Error synthesizing audio ({type(e).__name__}): {str(e)}"
        except Exception as e:
            return f"Unexpected error synthesizing audio ({type(e).__name__}): {str(e)}"
    
    def _save_binary_file(self, file_name, data):
        """
        Save binary data to a file.
        
        Args:
            file_name (str): Path to save the file
            data (bytes): Binary data to save
        """
        with open(file_name, "wb") as f:
            f.write(data)
        print(f"File saved to: {file_name}")
    
    def _convert_to_wav(self, audio_data, mime_type):
        """
        Generates a WAV file header for the given audio data and parameters.
        
        Args:
            audio_data (bytes): The raw audio data
            mime_type (str): Mime type of the audio data
            
        Returns:
            bytes: WAV formatted audio data
        """
        parameters = self._parse_audio_mime_type(mime_type)
        bits_per_sample = parameters["bits_per_sample"]
        sample_rate = parameters["rate"]
        num_channels = 1
        data_size = len(audio_data)
        bytes_per_sample = bits_per_sample // 8
        block_align = num_channels * bytes_per_sample
        byte_rate = sample_rate * block_align
        chunk_size = 36 + data_size  # 36 bytes for header fields before data chunk size
        
        # WAV header format: http://soundfile.sapp.org/doc/WaveFormat/
        header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF",          # ChunkID
            chunk_size,       # ChunkSize (total file size - 8 bytes)
            b"WAVE",          # Format
            b"fmt ",          # Subchunk1ID
            16,               # Subchunk1Size (16 for PCM)
            1,                # AudioFormat (1 for PCM)
            num_channels,     # NumChannels
            sample_rate,      # SampleRate
            byte_rate,        # ByteRate
            block_align,      # BlockAlign
            bits_per_sample,  # BitsPerSample
            b"data",          # Subchunk2ID
            data_size         # Subchunk2Size (size of audio data)
        )
        return header + audio_data
    
    def _parse_audio_mime_type(self, mime_type):
        """
        Parses bits per sample and rate from an audio MIME type string.
        
        Args:
            mime_type (str): The audio MIME type string (e.g., "audio/L16;rate=24000")
            
        Returns:
            dict: Dictionary with "bits_per_sample" and "rate" keys
        """
        bits_per_sample = 16
        rate = 24000
        
        # Extract rate from parameters
        parts = mime_type.split(";")
        for param in parts:
            param = param.strip()
            if param.lower().startswith("rate="):
                try:
                    rate_str = param.split("=", 1)[1]
                    rate = int(rate_str)
                except (ValueError, IndexError):
                    pass  # Keep rate as default
            elif param.startswith("audio/L"):
                try:
                    bits_per_sample = int(param.split("L", 1)[1])
                except (ValueError, IndexError):
                    pass  # Keep bits_per_sample as default
        
        return {"bits_per_sample": bits_per_sample, "rate": rate}


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
    
    # Example script for two speakers
    test_script = """
    Alex: Hi Jordan, how are you today? [pause]
    Jordan: I'm doing great, Alex! Thanks for asking. Just enjoying the sunshine. [soft laugh]
    Alex: That's wonderful to hear. Sunshine always lifts the spirits.
    Jordan: It really does. What are you up to?
    """
    
    synthesizer = AudioSynthesizer(api_key)
    output_path = synthesizer.synthesize_audio(
        test_script, 
        "test_multi_speaker_output.wav",
        model_name="gemini-2.5-flash-preview-tts",
        speaker1_name="Alex",
        speaker1_voice="Enceladus", # Or any from available_voices
        speaker2_name="Jordan",
        speaker2_voice="Puck"    # Or any from available_voices
    )
    print(f"Audio saved to: {output_path}")
