import serial
import os
import time

class SIM800CUploader:
    def __init__(self, port='COM10', baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.ser = None

    def connect(self):
        """Establish serial connection"""
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1
            )
            print(f"Connected to {self.port} at {self.baudrate} baud")
            self._send_at_command("AT")  # Test connection
            return True
        except Exception as e:
            print(f"Connection failed: {str(e)}")
            return False

    def _send_at_command(self, command, wait_for=None, timeout=5):
        """Send AT command and return response"""
        self.ser.write(f"{command}\r\n".encode())
        print(f"Sent: {command}")
        
        response = b''
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            if self.ser.in_waiting > 0:
                data = self.ser.read(self.ser.in_waiting)
                response += data
                if wait_for and wait_for.encode() in response:
                    break
        
        decoded = response.decode(errors='ignore').strip()
        print(f"Received: {decoded}")
        return decoded

    def upload_file(self, local_path, module_path):
        """Upload AMR file to module's internal storage"""
        try:
            # Verify local file exists
            if not os.path.exists(local_path):
                print(f"Error: Local file {local_path} not found")
                return False
            
            file_size = os.path.getsize(local_path)
            file_name = os.path.basename(module_path)
            
            # Create file on module
            create_cmd = f'AT+FSCREATE="{module_path}"'
            if "OK" not in self._send_at_command(create_cmd):
                print("File creation failed")
                return False
            
            # Prepare for write operation
            write_cmd = f'AT+FSWRITE="{module_path}",0,{file_size},100'
            response = self._send_at_command(write_cmd, wait_for="DOWNLOAD")
            
            if "DOWNLOAD" not in response:
                print("Failed to enter download mode")
                return False
            
            # Send file data
            with open(local_path, 'rb') as f:
                file_data = f.read()
                self.ser.write(file_data)
                print(f"Sent {len(file_data)} bytes of file data")
            
            # Verify write completion
            if "OK" in self._send_at_command("", timeout=10):
                print("File write successful")
                return self.verify_upload(module_path, file_size)
            
            return False
            
        except Exception as e:
            print(f"Upload failed: {str(e)}")
            return False

    def verify_upload(self, module_path, expected_size):
        """Verify file existence and size"""
        # Check file listing
        list_files = self._send_at_command('AT+FSLS="C:\\"')
        if module_path.split('\\')[-1] not in list_files:
            print("File not found in directory listing")
            return False
        
        # Check file size
        size_cmd = f'AT+FSIZE="{module_path}"'
        size_response = self._send_at_command(size_cmd)
        if f"+FSIZE: {expected_size}" in size_response:
            print("File size verification successful")
            return True
        
        print("File size mismatch")
        return False

if __name__ == "__main__":
    uploader = SIM800CUploader(port='COM10')  # Change to your COM port
    
    if uploader.connect():
        success = uploader.upload_file(
            local_path="Audio Files\audio2.amr",
            module_path="C:\\User\\audio2.amr"
        )
        
        if success:
            print("File upload and verification complete!")
        else:
            print("Upload failed. Check debug output.")
    else:
        print("Could not establish connection to module")
