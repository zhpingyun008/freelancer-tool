#!/usr/bin/env python3
"""Freelancer Tool MVP - AI Contract Generator + Quote Generator"""

import os
import json
import secrets
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

# ── Config ──────────────────────────────────────────────────────────────
_DK = os.environ.get("DEEPSEEK_API_KEY", "")
_DU = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
if not _DK:
    # Fallback: source from .env
    import subprocess
    r = subprocess.run(
        "bash -c 'source ~/.hermes/.env && echo \"$DEEPSEEK_API_KEY\"'",
        shell=True, capture_output=True, text=True, executable="/bin/bash"
    )
    _DK = r.stdout.strip()
    r2 = subprocess.run(
        "bash -c 'source ~/.hermes/.env && echo \"$DEEPSEEK_BASE_URL\"'",
        shell=True, capture_output=True, text=True, executable="/bin/bash"
    )
    _DU = r2.stdout.strip() or _DU

DEEPSEEK_API_KEY = _DK
DEEPSEEK_BASE_URL = _DU
DEEPSEEK_MODEL = "deepseek-chat"
FREE_USAGE_LIMIT = 3

# ── App Setup ───────────────────────────────────────────────────────────
app = FastAPI(
    title="自由职业者工具 - Freelancer Tool",
    description="AI驱动的合同生成与报价生成工具，专为自由职业者设计",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# ── Usage tracking (in-memory, resets on restart) ──────────────────────
usage_db: dict[str, int] = {}  # client_ip -> count this month


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _get_usage(ip: str) -> int:
    return usage_db.get(ip, 0)


def _increment_usage(ip: str) -> int:
    usage_db[ip] = usage_db.get(ip, 0) + 1
    return usage_db[ip]


# ── Request Models ──────────────────────────────────────────────────────
class ContractRequest(BaseModel):
    contract_type: str
    party_a: str
    party_b: str
    terms: str = ""


class QuoteRequest(BaseModel):
    service_description: str
    amount: float
    currency: str = "CNY"


# ── DeepSeek API Helper ─────────────────────────────────────────────────
async def call_deepseek(system_prompt: str, user_prompt: str) -> str:
    """Call DeepSeek API and return the response text."""
    if not DEEPSEEK_API_KEY:
        raise HTTPException(status_code=500, detail="DeepSeek API key not configured")

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{DEEPSEEK_BASE_URL}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": DEEPSEEK_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.7,
                "max_tokens": 4096,
            },
        )
    if resp.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"DeepSeek API error ({resp.status_code}): {resp.text}",
        )
    data = resp.json()
    return data["choices"][0]["message"]["content"]


# ── Routes ──────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def landing():
    return FileResponse(static_dir / "index.html")


@app.get("/generate-contract", response_class=HTMLResponse)
async def contract_page():
    return FileResponse(static_dir / "contract.html")


@app.get("/generate-quote", response_class=HTMLResponse)
async def quote_page():
    return FileResponse(static_dir / "quote.html")


@app.post("/api/generate-contract")
async def generate_contract(req: ContractRequest, request: Request):
    ip = _client_ip(request)
    usage = _get_usage(ip)
    if usage >= FREE_USAGE_LIMIT:
        return JSONResponse(
            status_code=403,
            content={
                "error": "free_limit_reached",
                "message": f"本月免费次数已用完（{FREE_USAGE_LIMIT}次），请升级到 Pro 版以继续使用。",
                "usage": usage,
                "limit": FREE_USAGE_LIMIT,
            },
        )

    system_prompt = """你是一位专业的法律合同撰写专家。根据用户提供的合同类型、签约方信息和条款要求，生成一份正式、专业、合法的中文合同文本。

合同应包括：
1. 合同标题
2. 合同编号（自动生成）
3. 签约方信息
4. 鉴于条款
5. 定义条款（如有需要）
6. 主要条款（逐条列出）
7. 违约责任
8. 争议解决
9. 其他条款
10. 签署栏

使用正式的法律语言，格式清晰，便于阅读。"""
    user_prompt = f"""请生成一份中文合同。

合同类型：{req.contract_type}
甲方：{req.party_a}
乙方：{req.party_b}
附加条款及要求：{req.terms}"""

    try:
        content = await call_deepseek(system_prompt, user_prompt)
        _increment_usage(ip)
        return {"success": True, "content": content, "usage": _get_usage(ip), "limit": FREE_USAGE_LIMIT}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-quote")
async def generate_quote(req: QuoteRequest, request: Request):
    ip = _client_ip(request)
    usage = _get_usage(ip)
    if usage >= FREE_USAGE_LIMIT:
        return JSONResponse(
            status_code=403,
            content={
                "error": "free_limit_reached",
                "message": f"本月免费次数已用完（{FREE_USAGE_LIMIT}次），请升级到 Pro 版以继续使用。",
                "usage": usage,
                "limit": FREE_USAGE_LIMIT,
            },
        )

    currency_symbols = {"CNY": "¥", "USD": "$", "EUR": "€"}
    symbol = currency_symbols.get(req.currency, req.currency)
    amount_str = f"{symbol}{req.amount:,.2f}"

    system_prompt = """你是一位专业的商业报价/服务报价撰写专家。根据用户提供的服务描述和金额，生成一份正式、专业、美观的中文报价单。

报价单应包括：
1. 报价单标题及编号
2. 日期信息
3. 服务提供方信息
4. 客户信息
5. 服务项目明细（拆分服务内容）
6. 价格明细
7. 付款条款
8. 有效期
9. 服务条款
10. 签名栏

格式清晰，专业美观。"""
    user_prompt = f"""请生成一份中文报价单。

服务描述：{req.service_description}
报价金额：{amount_str}
货币：{req.currency}"""

    try:
        content = await call_deepseek(system_prompt, user_prompt)
        _increment_usage(ip)
        return {"success": True, "content": content, "usage": _get_usage(ip), "limit": FREE_USAGE_LIMIT}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/usage")
async def get_usage(request: Request):
    ip = _client_ip(request)
    return {"usage": _get_usage(ip), "limit": FREE_USAGE_LIMIT}


# ── Run ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=True)
