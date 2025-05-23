"""
Auto Daddy - Test Script

This script tests the end-to-end functionality of the Auto Daddy ASMR audio generation tool.
"""

import os
import sys
import time

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auto_daddy import AutoDaddy

def test_auto_daddy():
    """Test the end-to-end functionality of Auto Daddy."""
    
    print("=== Auto Daddy End-to-End Test ===")
    
    # Check for API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable not set")
        print("Please set the environment variable and try again")
        return False
    
    # Create test output directory
    test_output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output")
    os.makedirs(test_output_dir, exist_ok=True)
    print(f"Test output directory: {test_output_dir}")
    
    try:
        # Initialize Auto Daddy
        print("\n1. Initializing Auto Daddy...")
        auto_daddy = AutoDaddy(api_key=api_key, output_dir=test_output_dir)
        print("✓ Initialization successful")
        
        # Test AI script generation with different lengths
        print("\n2. Testing AI script generation with different lengths...")
        lengths = ["short", "medium", "long"]
        for length in lengths:
            print(f"\n   Generating {length} script...")
            script = auto_daddy.generate_script(
                theme=f"relaxation and comfort for {length} test", 
                length=length
            )
            print(f"   ✓ {length.capitalize()} script generated ({len(script.split())} words)")
            
            # Save the script
            script_path = auto_daddy.save_script(f"test_script_{length}.txt")
            print(f"   ✓ Script saved to: {script_path}")
        
        # Test manual script input
        print("\n3. Testing manual script input...")
        manual_script = """
        This is a manually entered ASMR script.
        Let me comfort you and help you relax.
        Just listen to my voice and let all your worries fade away.
        """
        formatted_script = auto_daddy.set_manual_script(manual_script)
        print("✓ Manual script set and formatted")
        
        # Save the manual script
        manual_script_path = auto_daddy.save_script("test_script_manual.txt")
        print(f"✓ Manual script saved to: {manual_script_path}")
        
        # Test audio generation with different voices
        print("\n4. Testing audio generation with different voices...")
        voices = auto_daddy.get_available_voices()
        
        # Generate audio from AI script
        print("\n   Generating audio from AI script...")
        auto_daddy.generate_script(theme="bedtime relaxation", length="short")
        for voice in voices[:2]:  # Test with first two voices
            print(f"   Generating audio with {voice} voice...")
            audio_path = auto_daddy.generate_audio(voice=voice, output_filename=f"test_audio_{voice}.wav")
            print(f"   ✓ Audio generated: {audio_path}")
        
        # Generate audio from manual script
        print("\n   Generating audio from manual script...")
        auto_daddy.set_manual_script(manual_script)
        audio_path = auto_daddy.generate_audio(output_filename="test_audio_manual.wav")
        print(f"   ✓ Audio generated: {audio_path}")
        
        print("\n=== All tests completed successfully! ===")
        return True
        
    except Exception as e:
        print(f"\nERROR: Test failed with exception: {str(e)}")
        return False

if __name__ == "__main__":
    test_auto_daddy()
