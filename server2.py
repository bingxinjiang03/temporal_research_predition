import threading
import queue
import av
import os
import cv2
from av.error import InvalidDataError
import gradio as gr
import json
import socket
from flask import Flask, request, jsonify
from datetime import datetime
import process_action
from process_action import handle
from model_response import get_response
from rotatequeue import RotatingQueue
# 创建保存帧的文件夹
os.makedirs("memory", exist_ok=True)

# 队列和 socket 参数
data_queue = queue.Queue(maxsize=200)
HOST = "0.0.0.0"
PORT = 20001
BUFFER_SIZE = 65536

# 全局变量用于facereg注册请求
facereg_flag = threading.Event()
facereg_target_path = None

# 接收UDP视频数据线程
def socket_receiver():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
        
    sock.settimeout(0.1)  # 临时设置超时
    while True:
        try:
            sock.recvfrom(BUFFER_SIZE)  # 丢弃残留数据
        except socket.timeout:
            break  # 缓冲区已空
    sock.settimeout(None)  # 恢复阻塞模式
    print("start")
    while (True):
        data, _ = sock.recvfrom(BUFFER_SIZE)
        if data:
            try:
                data_queue.put(data, timeout=1)
            except queue.Full:
                print("[RECEIVER] Queue full, dropping packet")

# 解码帧线程
def frame_decoder():
    codec_ctx = av.codec.CodecContext.create('h264', 'r')
    frame_count = 0
    frame_buffer = []
    frame_paths = []

    global facereg_flag, facereg_target_path

    while True:
        try:
            h264_data = data_queue.get(timeout=1)
        except queue.Empty:
            continue
        try:
            packet = av.packet.Packet(h264_data)
            frames = codec_ctx.decode(packet)
        except InvalidDataError:
            continue
        except Exception as e:
            print(f"[DECODE ERROR] {e}")
            continue

        for frame in frames:
            frame_count += 1
            if frame_count % 5 == 0:
                img = frame.to_ndarray(format="bgr24")
                frame_buffer.append(img)
                if len(frame_buffer) == 1:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    folder_path = f"memory/memory_{timestamp}"
                    os.makedirs(folder_path, exist_ok=True)  # 创建文件夹
                frame_path = f"{folder_path}/img_{frame_count:05d}.jpg"
                cv2.imwrite(frame_path, img)
                frame_paths.append(frame_path)

                # ✅ 外部facereg保存触发
                if facereg_flag.is_set() and facereg_target_path:
                    cv2.imwrite(facereg_target_path, img)
                    print(f"[FACEREG] Saved requested frame to: {facereg_target_path}")
                    facereg_flag.clear()

                if len(frame_buffer) == 8:
                    resp = get_response(frame_paths).replace("json", '').replace("```", '').replace("\n", "").replace("”", '"').strip()
                    try:
                        result = json.loads(resp)
                        text = handle(result["关键事件"], result["事实"], frame_paths)
                        print(text)
                    except json.JSONDecodeError as e:
                        print(f"[PARSE ERROR] JSON解析失败，内容: {resp[:100]}...")

                    frame_buffer.clear()
                    frame_paths.clear()

# HTTP服务用于接收注册请求（/getface）
main_app = Flask("MainGetFaceApp")

@main_app.route('/getface', methods=['POST'])
def getface():
    global facereg_target_path
    data = request.get_json()
    if not data or 'name' not in data or 'path' not in data:
        return jsonify({"status": "error", "message": "Missing 'name' or 'path'"}), 400
    facereg_target_path = data['path']
    facereg_flag.set()
    print(f"[GETFACE] Received facereg request for {data['name']}, will save to {facereg_target_path}")
    return jsonify({"status": "success"}), 200

def run_main_http_server():
    main_app.run(host="0.0.0.0", port=9090)

# 启动线程
if __name__ == "__main__":
    t1 = threading.Thread(target=socket_receiver, daemon=True)
    t2 = threading.Thread(target=frame_decoder, daemon=True)
    t3 = threading.Thread(target=run_main_http_server, daemon=True)

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()
