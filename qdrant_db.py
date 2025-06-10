from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from datetime import datetime
import random
import secrets
import socket
import json

HOST = '0.0.0.0'
PORT = 9010  # 专属端口：事件写入数据库

client = QdrantClient(
    host="10.214.95.205",
    port=8333,
    timeout=30,
#    check_compatibility=False
)
base_url = "http://10.214.95.205:8000"

model_name = "bge-large-zh-v1.5"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)
model.eval()

def get_embedding(text):
    inputs = tokenizer(text, padding=True, truncation=True, return_tensors="pt", max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    embeddings = F.normalize(outputs.last_hidden_state[:, 0], p=2, dim=1)  # 使用 CLS 向量并归一化
    return embeddings

def insert_db(text,img_path):
        embeddings=get_embedding(text)
        img_url = f"{base_url}/frames/{img_path}"
        client.upsert(
        collection_name="video_memory",
        points=[
            {
                "id": secrets.randbelow(10**8),
                "vector": embeddings[0].tolist(),
                "payload": {
                    "text": text,
                    "timestamp": datetime.utcnow().isoformat(),
                    "image_url": img_url}
            }
        ]
    )


def run_write_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[事件写入数据库] Server 启动，监听端口 {PORT}",flush=True)
        while True:
            conn, addr = s.accept()
            with conn:
                data = conn.recv(4096).decode()
                if data:
                    try:
                        event = json.loads(data)
                        insert_db(event.get("事件"),event.get("path"))
                        print(f"[事件写入数据库]-{event.get('事件')}",flush=True)
                    except Exception as e:
                        print("❌ JSON 解析错误:", e)

if __name__ == '__main__':
    run_write_server()
