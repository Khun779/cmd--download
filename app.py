import os
import subprocess
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
# Use relative path for downloads folder
DOWNLOAD_FOLDER = "downloads"

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/download-video', methods=['POST'])
def download_video():
    try:
        # Get the video URL from frontend
        data = request.json
        video_url = data.get("video_url")
        if not video_url:
            return jsonify({"error": "No video URL provided"}), 400

        # Check if downloads folder exists, if not create it
        if not os.path.exists(DOWNLOAD_FOLDER):
            print(f"Creating downloads folder: {DOWNLOAD_FOLDER}")
            try:
                os.makedirs(DOWNLOAD_FOLDER)
            except Exception as e:
                print(f"Error creating downloads folder: {str(e)}")
                return jsonify({"error": "Could not create downloads folder"}), 500
        else:
            print(f"Using existing downloads folder: {DOWNLOAD_FOLDER}")

        # Commands to run as if in terminal
        commands = [
            f'cd {DOWNLOAD_FOLDER}',        # Navigate to downloads directory
            f'''yt-dlp --no-check-certificate --format best \
                --user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
                --referer "https://www.google.com/" \
                --verbose \
                "{video_url}" '''  # Added --verbose for more output
        ]

        # Combine commands with && to ensure they run in sequence
        if os.name == 'nt':  # Windows
            command = ' && '.join(commands)
            shell_cmd = f'cmd /c "{command}"'
        else:  # Linux/Unix
            command = ' && '.join(commands)
            shell_cmd = ['bash', '-c', command]  # Use list format for better escaping

        # Execute the commands
        print(f"Running commands:\n{command}")
        try:
            process = subprocess.Popen(
                shell_cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            # Print full output for debugging
            print(f"STDOUT:\n{stdout}")
            print(f"STDERR:\n{stderr}")

            if process.returncode != 0:
                error_msg = stderr.strip() if stderr else "Unknown error occurred"
                print(f"Download failed: {error_msg}")
                return jsonify({"error": f"Download failed: {error_msg}"}), 500

            # Check if any files were actually downloaded
            files = os.listdir(DOWNLOAD_FOLDER)
            if not files:
                return jsonify({"error": "No files were downloaded"}), 500

            print(f"Files in download folder: {files}")
            return jsonify({
                "message": "Video downloaded successfully", 
                "folder": os.path.abspath(DOWNLOAD_FOLDER),
                "files": files  # Add list of downloaded files to response
            }), 200

        except subprocess.SubprocessError as e:
            print(f"Error during download process: {str(e)}")
            return jsonify({"error": f"Download process failed: {str(e)}"}), 500

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    # Verify yt-dlp installation on startup
    try:
        subprocess.run(['yt-dlp', '--version'], 
                      capture_output=True, 
                      text=True, 
                      check=True)
    except Exception as e:
        print("Error: yt-dlp is not properly installed or not in PATH")
        print("Please install yt-dlp using: pip install --upgrade yt-dlp")
        exit(1)
    
    # Ensure downloads folder exists at startup
    if not os.path.exists(DOWNLOAD_FOLDER):
        try:
            os.makedirs(DOWNLOAD_FOLDER)
            print(f"Created downloads folder: {DOWNLOAD_FOLDER}")
        except Exception as e:
            print(f"Warning: Could not create downloads folder: {str(e)}")
    
    app.run(debug=True)