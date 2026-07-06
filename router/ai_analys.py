import httpx
import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from util.security import get_current_user

router = APIRouter(prefix="/api/ai", tags=["ai_analysis"])

QWEN_API_KEY = "your_api_key_here"
QWEN_API_URL = "URL地址"
QWEN_MODEL = "使用的ai模型"

class AnalysisRequest(BaseModel):
    content: str


async def stream_qwen_response(content: str):
    """
    生成器函数：一个字一个字地把 AI 回答推给前端

    这函数用 async yield，就像水龙头一样：
    每次 yield 一个 SSE 格式的字符串，前端就能收到一个片段
    """
    headers = {
        "Authorization": f"Bearer {QWEN_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": QWEN_MODEL,
        "messages": [
            {"role": "system", "content": "你是一个智能助手，帮助用户分析和解释消息内容。请简洁、清晰地给出分析。"},
            {"role": "user", "content": content}
        ],
        "stream": True  # ← 流式：逐字返回
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        # 关键：使用 stream() 获取流式响应，逐块读取
        async with client.stream("POST", QWEN_API_URL, json=payload, headers=headers) as response:
            # response.aiter_lines() 是异步迭代器，每次读一行
            async for line in response.aiter_lines():
                if not line.strip():
                    continue  # 跳过空行

                # SSE 格式：每行以 "data: " 开头
                if line.startswith("data: "):
                    data_str = line[6:]  # 去掉 "data: " 前缀

                    if data_str == "[DONE]":
                        break  # 千问发完了

                    try:
                        chunk = json.loads(data_str)
                        # 从返回块里提取本次新增的文字
                        delta_content = chunk["choices"][0]["delta"].get("content", "")
                        if delta_content:
                            # 推给前端，SSE 格式
                            yield f"data: {json.dumps({'content': delta_content}, ensure_ascii=False)}\n\n"
                    except (json.JSONDecodeError, KeyError):
                        continue  # 解析失败就跳过这一块


@router.post("/analyze/stream")
async def analyze_message_stream(req: AnalysisRequest, user_id: int = Depends(get_current_user)):
    """
    流式调用千问，AI 一个字一个字地回答
    前端能实时看到 AI 正在"打字"
    """
    return StreamingResponse(
        stream_qwen_response(req.content),
        media_type="text/event-stream"  # ← 告诉前端这是 SSE 流
    )
