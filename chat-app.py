import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from transformers import AutoProcessor
from vllm import LLM, SamplingParams
from qwen_vl_utils import process_vision_info
import uvicorn
import multiprocessing
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime


logging.basicConfig(
    handlers=[RotatingFileHandler('app.log', maxBytes=10 * 1024 * 1024, backupCount=5)],
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 设置 CUDA 多进程启动方法（必须放前面）
multiprocessing.set_start_method("spawn", force=True)
os.environ["VLLM_WORKER_MULTIPROC_METHOD"] = "spawn"
os.environ["HF_HUB_OFFLINE"] = "1"  # 强制离线模式
os.environ["CUDA_MODULE_LOADING"] = "LAZY"
app = FastAPI()

# 允许跨域（按需配置）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = None
processor = None
sampling_params = None


@app.post("/generate")
async def generate(request: Request):
    try:
        logger.info("REQUEST RECEIVED | client: %s", request.client.host)
        start_time = datetime.now()

        data = await request.json()
        messages = data.get("messages", [])
        
        # 处理多模态输入
        prompt = processor.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        image_inputs, video_inputs, video_kwargs = process_vision_info(messages, return_video_kwargs=True)
        mm_data = {}
        if image_inputs is not None:
            mm_data["image"] = image_inputs
        if video_inputs is not None:
            mm_data["video"] = video_inputs

        # 生成响应
        outputs = llm.generate(
            [{
                "prompt": prompt,
                "multi_modal_data": mm_data,
                "mm_processor_kwargs": video_kwargs,
            }],
            sampling_params=sampling_params
        )

        end_time = datetime.now()
        logger.info(
            "INFERENCE COMPLETE | duration=%.3fs",
            (end_time - start_time).total_seconds()
        )
        return {"response": outputs[0].outputs[0].text}
    
    except Exception as e:
        logger.error("ERROR: %s", str(e), exc_info=True)
        return {"error": str(e)}


def init_model():
    global llm, processor, sampling_params
    MODEL_PATH = "Qwen2.5-VL-32B-Instruct-AWQ"

    llm = LLM(
        model=MODEL_PATH,
        quantization="awq",
        dtype="float16",
        gpu_memory_utilization=0.95,
        max_model_len=16000,
        max_num_seqs=1,
        limit_mm_per_prompt={"image": 10, "video": 1},
        tensor_parallel_size=2,
    )

    processor = AutoProcessor.from_pretrained(MODEL_PATH)
    sampling_params = SamplingParams(
        temperature=0.0,
        top_p=1,
        repetition_penalty=1.05,
        max_tokens=256,
        stop_token_ids=[151643],
    )

if __name__ == "__main__":
    init_model()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9998,
        workers=1,  # 多worker可能导致显存不足
    )
