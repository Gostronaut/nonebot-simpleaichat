from nonebot import on_message, get_driver
import random
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.adapters.onebot.v11.permission import GROUP, PRIVATE_FRIEND
import httpx
import json
import os
from pathlib import Path
from .manager import add_whitelist,remove_whitelist

# 配置API Key和API地址
API_KEYS = ["sk-A1TAnpIKyJ7st9Ea943d081aC96f4f539f296f6870D04b1e"]
API_URL = "https://api.openai99.top/v1/chat/completions"

# 全局人设
GLOBAL_PROMPT = "你是一个智能ai机器人"
# 配置上下文长度和最大token数量
CONTEXT_LENGTH = 5
MAX_TOKENS = 250

config_dir = Path("config/aichat").absolute()
config_dir.mkdir(parents=True, exist_ok=True)

# 创建白名单文件
whitelist_file_path = config_dir / "whitelist.json"
if not whitelist_file_path.exists():
    with open(whitelist_file_path, "w", encoding="utf-8") as f:
        json.dump([], f)  # 初始化为空白名单

# 数据存储目录
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# 创建消息处理器
chat = on_message(priority=49, rule=to_me(), permission=GROUP)

@chat.handle()
async def handle_chat(bot: Bot, event: Event):
    user_id = event.get_user_id()
    group_id = event.group_id  # 获取群组ID
    user_message = event.get_message()

    # 检查群组是否在白名单中
    if not is_in_whitelist(group_id):
        await chat.send("抱歉，这个群组不在白名单中，无法进行对话。")
        return

    # 加载上下文
    context = load_context(user_id)

    # 更新上下文
    context.append({"role": "user", "content": str(user_message)})

    # 如果上下文长度超过配置的上下文数量，删除旧的记录
    if len(context) > CONTEXT_LENGTH * 2:  # 考虑到用户和助手的消息
        context = context[-CONTEXT_LENGTH * 2:]

    # 构建请求数据，始终包含全局人设
    request_data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "system", "content": GLOBAL_PROMPT}] + context[-CONTEXT_LENGTH:],
        "max_tokens": MAX_TOKENS
    }

    # 随机选择一个API Key
    api_key = random.choice(API_KEYS)

    # 发送请求到API
    async with httpx.AsyncClient() as client:
        response = await client.post(
            API_URL,
            json=request_data,
            headers={"Authorization": f"Bearer {api_key}"}
        )

        if response.status_code == 200:
            data = response.json()
            assistant_message = data["choices"][0]["message"]["content"]
            await chat.send(assistant_message)

            # 更新上下文
            context.append({"role": "assistant", "content": assistant_message})
            save_context(user_id, context)
        else:
            await chat.send("抱歉，我现在无法处理您的消息。")

def is_in_whitelist(group_id):
    with open(whitelist_file_path, "r", encoding="utf-8") as f:
        whitelist = json.load(f)
    return str(group_id) in whitelist  # 将 group_id 转换为字符串进行比较

def load_context(user_id):
    file_path = os.path.join(DATA_DIR, f"{user_id}.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            context = json.load(f)
            return context
    return []

def save_context(user_id, context):
    file_path = os.path.join(DATA_DIR, f"{user_id}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(context, f, ensure_ascii=False, indent=4)
