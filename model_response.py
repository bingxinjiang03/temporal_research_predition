import base64
import os
import time
import json
from openai import OpenAI
import requests
import cv2
import numpy as np
from pathlib import Path
def concat_4_equal_images(imgs, add_numbering=True):
    # 读取所有图片并添加编号
    images=[]
    for i, img in enumerate(imgs):
        if add_numbering:
            h, w = img.shape[:2]
            font_scale = h / 700
            thickness = max(1, int(font_scale * 2))
            # 添加序号标签（带半透明背景）
            label = f"No.{i+1}"
            (text_w, text_h), _ = cv2.getTextSize(label, 
                                                 cv2.FONT_HERSHEY_SIMPLEX, 
                                                 font_scale, thickness)        
            
	    # 文字背景框
            cv2.rectangle(img, 
                         (10, 10), 
                         (text_w + 10, text_h + 10), 
                         (0, 0, 0), -1)
            
	    # 白色文字
            cv2.putText(img, label, 
                       (10, 10 + text_h), 
                       cv2.FONT_HERSHEY_SIMPLEX, 
                       font_scale, (255, 255, 255), thickness)
        images.append(img)
    # 拼接操作
    top_row = cv2.hconcat([images[0], images[1]])
    bottom_row = cv2.hconcat([images[2], images[3]])
    final_img = cv2.vconcat([top_row, bottom_row])
    return final_img



prompt = """你是一名视频内容分析AI，请基于视频严格完成结构化分析任务:
##任务要求
· 客观概括当前片段的核心事实,主要包括人物、环境、关键物品、主要行为.
· 精准识别以下关键事件:
  1.有人招手 
  2.有人玩手机
  3.不小心摔跤
  4.有人抽烟
  5.有人吃东西或喝水
##输出规范(严格遵循JSON格式)：
{
"事实": "请客观的描述人物在该片段中的主要行为过程,所有信息必须基于图像内容推理得出,尽可能的详细",
"关键事件": "选择最多一个关键事件，直接填序号。完全无匹配则填'无'",
}
##示例输入：
前情提要:地铁上，一个穿黑色外套的年轻人坐下来，手伸进了自己的口袋。
视频帧:
##示例回答：
{
"事实":"地铁车厢内，穿黑色外套的年轻人低头玩手机，屏幕亮着",
"关键事件":"2",
}
请严格按照json格式回答
"""



def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def get_response(imgs):
    video=[]
    for img in imgs:
        img=image_to_base64(img)
        v=f"data:image/jpeg;base64,{img}"
        video.append(v)
    data={
        "messages":[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": [
                {"type": "text", "text":f"{prompt}"},
                {
                    "type": "video",
                    "video":video,
                }
                ]
            },
        ]
    }
    #start = time.time()
    response =requests.post("http://localhost:9998/generate", json=data)
    response.raise_for_status()
    #end = time.time()
    #print(f"运行时间: {end - start:.6f} 秒")
    #print(response.json())
    return response.json()['response']

path="frames/img_00001.jpg"
#get_response2(path,"剧情开始")


