import os
import subprocess
import sys

def debug_print(msg):
    print(f"[DEBUG] {msg}")

def check_dependencies():
    """Check for required dependencies and install them if missing."""
    try:
        import pydub
        debug_print("pydub is already installed.")
    except ImportError:
        debug_print("Installing pydub...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pydub"])
        debug_print("pydub installed successfully.")
        import pydub  # Try importing again after installation
    
    # Check if ffmpeg is installed
    try:
        result = subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            debug_print("ffmpeg is already installed.")
            return True
    except FileNotFoundError:
        debug_print("ffmpeg not found.")
        
        # Instructions for installing ffmpeg
        print("\nFFmpeg is required but not found. Please install FFmpeg:")
        print("1. Download from https://ffmpeg.org/download.html")
        print("2. Add it to your system PATH")
        print("3. Restart your terminal/IDE and try again")
        return False
    
    return True

def convert_to_amr(input_file, output_file=None):
    """Convert audio file to AMR format using FFmpeg."""
    if not check_dependencies():
        debug_print("Dependencies not satisfied. Cannot convert file.")
        return None
    
    if output_file is None:
        # Create output filename based on input
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}.amr"
    
    try:
        # Use ffmpeg for conversion
        debug_print(f"Converting {input_file} to AMR format...")
        cmd = ["ffmpeg", "-i", input_file, "-ar", "8000", "-ab", "12.2k", "-ac", "1", "-y", output_file]
        
        # Run conversion
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if result.returncode != 0:
            debug_print(f"Error during conversion: {result.stderr.decode()}")
            return None
            
        debug_print(f"Conversion successful. Output file: {output_file}")
        return output_file
    
    except Exception as e:
        debug_print(f"Error converting file: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        convert_to_amr(input_file, output_file)
    else:
        print("Usage: python convert_to_amr.py <input_file> [output_file]")
