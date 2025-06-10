import socket
import json
from datetime import datetime
import requests
API_URL = "http://10.214.95.205:8010/api/v1/face/query"  # 根据部署端口替换
def send_event(event, person, port):
    HOST = '127.0.0.1'
    event = {
        "事实":event,
        "人物": person,
        "时间": datetime.now().isoformat()
    }
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, port))
        s.sendall(json.dumps(event).encode())


def handle(action,event,frames):
    text="无动作"
    name="陌生人"
    if str(action)=="1":
        for frame in frames:
            # 打开图片并发送 POST 请求
            with open(frame, "rb") as f:
                files = {"file": (frame, f, "image/jpeg")}
                response = requests.post(API_URL,  files=files)
            if(response.status_code==200):
                name=response.json()["name"]
                send_event(event,name,9001)           
                text=f"""你好啊!!{name}"""
                break
    if str(action)=="2":
        text=f"""别玩手机了!!"""
        send_event(event,name,9002)
    if str(action)=="3":
        text=f"""你要小心呀"""
        send_event(event,name,9003)
    if str(action)=="4":
        text="不要在公共场合抽烟哦"
        send_event(event,name,9004)
    if str(action)=="5":
        text=f"""别噎着了!!"""
        send_event(event,name,9005)    
    return text
