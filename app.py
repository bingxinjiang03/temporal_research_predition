
from flask import Flask, send_from_directory
import os

app = Flask(__name__)

# 本地视频文件路径
VIDEO_FOLDER = os.path.join(os.path.dirname(__file__), 'videos')
IMAGE_FOLDER = os.path.join(os.path.dirname(__file__), 'user_faces')
FRAMES_FOLDER = os.path.join(os.path.dirname(__file__), 'frames')
@app.route('/user_faces/<path:filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

@app.route('/frames/<path:filename>')
def serve_frame(filename):
        return send_from_directory(FRAMES_FOLDER, filename)

@app.route('/videos/<path:filename>')
def serve_video(filename):
	return send_from_directory(VIDEO_FOLDER, filename)


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8000)
