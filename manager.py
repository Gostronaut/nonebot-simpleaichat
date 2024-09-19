from nonebot import on_command
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import Bot, Event
import json
from pathlib import Path

# 白名单文件路径
config_dir = Path("config/aichat").absolute()
whitelist_file_path = config_dir / "whitelist.json"

# 加载白名单
def load_whitelist():
    with open(whitelist_file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# 保存白名单
def save_whitelist(whitelist):
    with open(whitelist_file_path, "w", encoding="utf-8") as f:
        json.dump(whitelist, f, ensure_ascii=False, indent=4)

# 命令：添加聊天白名单
add_whitelist = on_command("添加聊天白名单", permission=SUPERUSER)

@add_whitelist.handle()
async def handle_add_whitelist(bot: Bot, event: Event):
    message = str(event.get_message()).strip()
    group_id = message.replace("添加聊天白名单", "").strip()
    
    if not group_id.isdigit():
        await add_whitelist.finish("请输入正确的群号。")
    
    whitelist = load_whitelist()
    if group_id not in whitelist:
        whitelist.append(group_id)
        save_whitelist(whitelist)
        await add_whitelist.finish(f"群组 {group_id} 已添加到白名单。")
    else:
        await add_whitelist.finish(f"群组 {group_id} 已在白名单中。")

# 命令：移出聊天白名单
remove_whitelist = on_command("移出聊天白名单", permission=SUPERUSER)

@remove_whitelist.handle()
async def handle_remove_whitelist(bot: Bot, event: Event):
    message = str(event.get_message()).strip()
    group_id = message.replace("移出聊天白名单", "").strip()
    
    if not group_id.isdigit():
        await remove_whitelist.finish("请输入正确的群号。")
    
    whitelist = load_whitelist()
    if group_id in whitelist:
        whitelist.remove(group_id)
        save_whitelist(whitelist)
        await remove_whitelist.finish(f"群组 {group_id} 已从白名单中移出。")
    else:
        await remove_whitelist.finish(f"群组 {group_id} 不在白名单中。")

# 命令：查看所有白名单
view_whitelist = on_command("查看所有白名单", permission=SUPERUSER)

@view_whitelist.handle()
async def handle_view_whitelist(bot: Bot, event: Event):
    whitelist = load_whitelist()
    if whitelist:
        await view_whitelist.finish("当前白名单中的群组ID有：\n" + "\n".join(whitelist))
    else:
        await view_whitelist.finish("白名单中没有任何群组。")
