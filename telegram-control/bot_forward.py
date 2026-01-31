#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
消息转发Bot - 直接把消息传给Claude Code处理
"""

import os
import sys
import json
import logging
import subprocess
import tempfile
from pathlib import Path

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
except ImportError:
    print("Error: python-telegram-bot not installed")
    sys.exit(1)

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')
LOG_FILE = os.path.join(os.path.dirname(__file__), 'bot_forward.log')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ForwardBot:
    """转发Bot - 把消息直接传给Claude Code"""

    def __init__(self):
        self.config = self.load_config()
        self.request_dir = Path(tempfile.gettempdir()) / 'claude_requests'
        self.request_dir.mkdir(exist_ok=True)
        self.response_dir = Path(tempfile.gettempdir()) / 'claude_responses'
        self.response_dir.mkdir(exist_ok=True)

        # 存储用户的文件选择状态 {user_id: {'file_list': [], 'selected': set(), 'page': 0}}
        self.user_selections = {}

        logger.info("ForwardBot initialized")

    def load_config(self):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    def check_permission(self, user_id):
        allowed = self.config.get('allowed_users', [])
        if not allowed:
            configured_id = self.config.get('chat_id')
            return str(user_id) == str(configured_id)
        return str(user_id) in allowed

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理消息 - 转发给Claude Code"""
        text = update.message.text

        if not self.check_permission(update.effective_user.id):
            await update.message.reply_text("No permission")
            return

        logger.info(f"收到消息: {text}")

        try:
            # 1. 创建请求文件
            request_id = f"req_{update.update_id}"
            request_file = self.request_dir / f"{request_id}.txt"

            request_data = {
                'message': text,
                'user_id': update.effective_user.id,
                'chat_id': update.effective_chat.id,
                'username': update.effective_user.username,
                'timestamp': update.message.date.isoformat()
            }

            with open(request_file, 'w', encoding='utf-8') as f:
                json.dump(request_data, f, ensure_ascii=False, indent=2)

            logger.info(f"请求已保存: {request_file}")
            await update.message.reply_text(f"[转发] 已发送给Claude Code...")

            # 2. 等待Claude Code处理
            # (Claude Code会监控request_dir，处理后写入response_dir)

            # 3. 轮询等待响应
            response_file = self.response_dir / f"{request_id}.txt"
            max_wait = 60  # 最多等60秒
            waited = 0

            while waited < max_wait:
                if response_file.exists():
                    with open(response_file, 'r', encoding='utf-8') as f:
                        response_data = json.load(f)

                    # 发送响应
                    if response_data.get('success'):
                        result = response_data.get('result', '')
                        file_list = response_data.get('file_list')  # 文件列表

                        # 如果需要发送文件
                        send_file_path = response_data.get('send_file')
                        if send_file_path and os.path.exists(send_file_path):
                            # 先发送文本消息
                            if result:
                                await update.message.reply_text(f"[Claude Code]\n{result}")

                            # 发送文件
                            logger.info(f"发送文件: {send_file_path}")
                            try:
                                # 判断文件类型
                                file_ext = Path(send_file_path).suffix.lower()

                                # 视频文件
                                if file_ext in ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm']:
                                    with open(send_file_path, 'rb') as f:
                                        await update.message.reply_video(f, caption=Path(send_file_path).name)
                                # 音频文件
                                elif file_ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a']:
                                    with open(send_file_path, 'rb') as f:
                                        await update.message.reply_audio(f, caption=Path(send_file_path).name)
                                # 图片文件
                                elif file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                                    with open(send_file_path, 'rb') as f:
                                        await update.message.reply_photo(f, caption=Path(send_file_path).name)
                                # 其他文件作为文档发送
                                else:
                                    with open(send_file_path, 'rb') as f:
                                        await update.message.reply_document(f, caption=Path(send_file_path).name)

                                logger.info(f"文件发送成功: {send_file_path}")
                            except Exception as e:
                                logger.error(f"发送文件失败: {e}")
                                await update.message.reply_text(f"[错误] 发送文件失败: {str(e)[:100]}")

                        # 如果有文件列表，创建分页的内联按钮
                        elif file_list:
                            user_id = update.effective_user.id

                            # 保存文件列表到用户状态
                            self.user_selections[user_id] = {
                                'file_list': file_list,
                                'selected': set(),  # 存储选中的文件索引
                                'page': 0
                            }

                            # 创建第一页的按钮界面
                            await self.send_file_list_page(update.message, user_id, result)

                        else:
                            # 只发送文本消息
                            await update.message.reply_text(f"[Claude Code]\n{result}")

                        # 处理其他文件列表（如果有）
                        if 'files' in response_data:
                            for file_path in response_data['files']:
                                if os.path.exists(file_path):
                                    with open(file_path, 'rb') as f:
                                        await update.message.reply_document(f)
                    else:
                        error = response_data.get('error', '未知错误')
                        await update.message.reply_text(f"[错误] {error}")

                    # 清理文件
                    response_file.unlink()
                    request_file.unlink()

                    logger.info(f"响应已发送")
                    return

                await asyncio.sleep(1)
                waited += 1

            # 超时
            await update.message.reply_text("[超时] Claude Code未响应")
            request_file.unlink()

        except Exception as e:
            logger.error(f"处理消息失败: {e}")
            await update.message.reply_text(f"[错误] {e}")

    async def start(self, update, context):
        await update.message.reply_text(
            " Claude Code转发Bot\n\n"
            "你的消息会直接传给Claude Code处理\n"
            "请用自然语言描述你的需求"
        )

    async def help_cmd(self, update, context):
        await update.message.reply_text(
            " Claude Code转发Bot\n\n"
            "直接用自然语言说话即可:\n"
            "• 在桌面新建test.txt\n"
            "• 列出桌面文件\n"
            "• ai助手.txt写入123456\n\n"
            "也可以直接发送文件给我，我会保存到电脑！"
        )

    async def send_file_list_page(self, message, user_id, header_text):
        """发送文件列表的某一页"""
        if user_id not in self.user_selections:
            return

        user_data = self.user_selections[user_id]
        file_list = user_data['file_list']
        selected = user_data['selected']
        page = user_data['page']

        # 每页显示16个文件（8行×2列）
        PAGE_SIZE = 16
        total_pages = (len(file_list) + PAGE_SIZE - 1) // PAGE_SIZE

        # 计算当前页的文件范围
        start_idx = page * PAGE_SIZE
        end_idx = min(start_idx + PAGE_SIZE, len(file_list))
        current_files = file_list[start_idx:end_idx]

        # 创建内联键盘
        keyboard = []

        # 文件选择按钮（两列布局）
        for idx in range(0, len(current_files), 2):
            row = []

            # 第一个文件
            if idx < len(current_files):
                global_idx = start_idx + idx
                filename = current_files[idx]['name']
                display_name = filename[:20] + '...' if len(filename) > 20 else filename
                status = '✅ ' if global_idx in selected else '⬜ '
                row.append(InlineKeyboardButton(f"{status}{display_name}", callback_data=f"select_{global_idx}"))

            # 第二个文件
            if idx + 1 < len(current_files):
                global_idx = start_idx + idx + 1
                filename = current_files[idx + 1]['name']
                display_name = filename[:20] + '...' if len(filename) > 20 else filename
                status = '✅ ' if global_idx in selected else '⬜ '
                row.append(InlineKeyboardButton(f"{status}{display_name}", callback_data=f"select_{global_idx}"))

            keyboard.append(row)

        # 分页按钮（左右对齐）
        nav_row = []
        if page > 0:
            nav_row.append(InlineKeyboardButton("⬅️ 上一页", callback_data=f"page_{page-1}"))
        else:
            nav_row.append(InlineKeyboardButton(" ", callback_data="info"))  # 占位
        if page < total_pages - 1:
            nav_row.append(InlineKeyboardButton("下一页 ➡️", callback_data=f"page_{page+1}"))
        if nav_row:
            keyboard.append(nav_row)

        # 快捷操作按钮
        action_row = [
            InlineKeyboardButton(f"📤 发送选中({len(selected)})", callback_data="action_send"),
            InlineKeyboardButton("📋 复制信息", callback_data="action_copy_info"),
            InlineKeyboardButton("🗑️ 删除", callback_data="action_delete"),
            InlineKeyboardButton("❌ 取消", callback_data="action_cancel")
        ]
        keyboard.append(action_row)

        reply_markup = InlineKeyboardMarkup(keyboard)

        # 发送或编辑消息
        text = f"{header_text}\n\n已选择: {len(selected)} 个文件"
        try:
            # 尝试编辑现有消息
            if hasattr(message, 'edit_text'):
                await message.edit_text(text, reply_markup=reply_markup)
            else:
                await message.reply_text(text, reply_markup=reply_markup)
        except Exception as e:
            # 如果编辑失败，发送新消息
            logger.info(f"编辑消息失败，发送新消息: {e}")
            await message.reply_text(text, reply_markup=reply_markup)

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理内联按钮点击"""
        query = update.callback_query
        user_id = update.effective_user.id
        await query.answer()  # 确认收到按钮点击

        try:
            callback_data = query.data
            logger.info(f"按钮点击: {callback_data}")

            # 分页按钮
            if callback_data.startswith('page_'):
                if user_id not in self.user_selections:
                    await query.message.reply_text("[提示] 此会话已结束，请重新发送「列出桌面文件」")
                    return
                new_page = int(callback_data.split('_')[1])
                self.user_selections[user_id]['page'] = new_page
                # 重新构建header文本
                file_list = self.user_selections[user_id]['file_list']
                header_text = f"[列表] Desktop: (共{len(file_list)}项)"
                for f in file_list[:5]:  # 只显示前5个文件
                    header_text += f"\n  [文件] {f['name']} ({f['size']})"
                if len(file_list) > 5:
                    header_text += f"\n  ... 还有{len(file_list)-5}个文件"
                await self.send_file_list_page(query.message, user_id, header_text)

            # 选择/取消选择文件
            elif callback_data.startswith('select_'):
                if user_id not in self.user_selections:
                    await query.message.reply_text("[提示] 此会话已结束，请重新发送「列出桌面文件」")
                    return
                file_idx = int(callback_data.split('_')[1])
                selected = self.user_selections[user_id]['selected']
                # 切换选中状态
                if file_idx in selected:
                    selected.remove(file_idx)
                else:
                    selected.add(file_idx)

                # 重新构建header文本并刷新页面
                file_list = self.user_selections[user_id]['file_list']
                header_text = f"[列表] Desktop: (共{len(file_list)}项)"
                await self.send_file_list_page(query.message, user_id, header_text)

            # 复制文件名
            elif callback_data.startswith('copy_'):
                file_idx = int(callback_data.split('_')[1])
                if user_id in self.user_selections:
                    file_list = self.user_selections[user_id]['file_list']
                    if file_idx < len(file_list):
                        filename = file_list[file_idx]['name']
                        await query.message.reply_text(
                            f"[文件名已复制]\n{filename}\n\n你可以直接说: 发送 {filename}"
                        )

            # 快捷操作：发送选中的文件
            elif callback_data == 'action_send':
                if user_id not in self.user_selections:
                    return

                selected = self.user_selections[user_id]['selected']
                file_list = self.user_selections[user_id]['file_list']

                if not selected:
                    await query.message.reply_text("[提示] 请先选择文件（点击文件名前的方框）")
                    return

                # 发送所有选中的文件
                success_count = 0
                for file_idx in selected:
                    if file_idx < len(file_list):
                        file_path = file_list[file_idx]['path']
                        filename = file_list[file_idx]['name']

                        if os.path.exists(file_path):
                            try:
                                file_ext = Path(file_path).suffix.lower()

                                # 根据文件类型发送
                                if file_ext in ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm']:
                                    with open(file_path, 'rb') as f:
                                        await query.message.reply_video(f, caption=filename)
                                elif file_ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a']:
                                    with open(file_path, 'rb') as f:
                                        await query.message.reply_audio(f, caption=filename)
                                elif file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                                    with open(file_path, 'rb') as f:
                                        await query.message.reply_photo(f, caption=filename)
                                else:
                                    with open(file_path, 'rb') as f:
                                        await query.message.reply_document(f, caption=filename)

                                success_count += 1
                                logger.info(f"已发送: {file_path}")
                            except Exception as e:
                                logger.error(f"发送失败: {file_path}, 错误: {e}")
                                await query.message.reply_text(f"[错误] 发送 {filename} 失败: {str(e)[:50]}")

                await query.message.reply_text(f"[OK] 已发送 {success_count}/{len(selected)} 个文件")
                # 清除选择状态并删除旧消息的按钮
                try:
                    await query.message.edit_reply_markup(reply_markup=None)
                except:
                    pass
                del self.user_selections[user_id]

            # 快捷操作：删除选中的文件
            elif callback_data == 'action_delete':
                if user_id not in self.user_selections:
                    return

                selected = self.user_selections[user_id]['selected']
                file_list = self.user_selections[user_id]['file_list']

                if not selected:
                    await query.message.reply_text("[提示] 请先选择文件")
                    return

                # 删除选中的文件
                deleted_count = 0
                for file_idx in list(selected):
                    if file_idx < len(file_list):
                        file_path = file_list[file_idx]['path']
                        filename = file_list[file_idx]['name']

                        try:
                            if os.path.exists(file_path):
                                os.remove(file_path)
                                deleted_count += 1
                                logger.info(f"已删除: {file_path}")
                        except Exception as e:
                            logger.error(f"删除失败: {file_path}, 错误: {e}")

                await query.message.reply_text(f"[OK] 已删除 {deleted_count}/{len(selected)} 个文件")
                # 清除选择状态并删除旧消息的按钮
                try:
                    await query.message.edit_reply_markup(reply_markup=None)
                except:
                    pass
                del self.user_selections[user_id]

            # 取消操作
            elif callback_data == 'action_cancel':
                if user_id in self.user_selections:
                    del self.user_selections[user_id]
                try:
                    await query.message.edit_reply_markup(reply_markup=None)
                except:
                    pass
                await query.message.reply_text("[已取消] 文件选择已清除")

            # 复制文件信息
            elif callback_data == 'action_copy_info':
                if user_id not in self.user_selections:
                    await query.message.reply_text("[提示] 此会话已结束，请重新发送「列出桌面文件」")
                    return

                selected = self.user_selections[user_id]['selected']
                file_list = self.user_selections[user_id]['file_list']

                if not selected:
                    await query.message.reply_text("[提示] 请先选择文件（点击文件名前的方框）")
                    return

                # 复制所有选中文件的信息
                info_text = f"[文件信息] 已选择 {len(selected)} 个文件\n\n"
                for idx in sorted(selected):
                    if idx < len(file_list):
                        file_info = file_list[idx]
                        info_text += f"📄 {file_info['name']}\n"
                        info_text += f"   路径: {file_info['path']}\n"
                        info_text += f"   大小: {file_info['size']}\n\n"

                await query.message.reply_text(info_text)

            # 信息按钮（不做任何事）
            elif callback_data == 'info':
                pass

        except Exception as e:
            logger.error(f"处理按钮点击失败: {e}")
            import traceback
            traceback.print_exc()
            await query.message.reply_text(f"[错误] 操作失败: {str(e)[:100]}")

    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理接收的文件 - 支持所有格式"""
        try:
            # 获取文件信息
            document = update.message.document
            photo = update.message.photo
            video = update.message.video
            audio = update.message.audio
            voice = update.message.voice

            filename = None
            file_size = None
            file_type = None
            file_obj = None

            # 1. 视频处理
            if video:
                file_size = video.file_size
                file_type = "视频"
                # 获取视频文件
                file_obj = await video.get_file()
                # 保留原文件名或生成新文件名
                if hasattr(video, 'file_name') and video.file_name:
                    filename = video.file_name
                else:
                    filename = f"video_{update.update_id}.mp4"
                logger.info(f"收到视频: {filename}, 大小: {file_size}字节")

            # 2. 音频处理
            elif audio:
                file_size = audio.file_size
                file_type = "音频"
                file_obj = await audio.get_file()
                if hasattr(audio, 'file_name') and audio.file_name:
                    filename = audio.file_name
                else:
                    filename = f"audio_{update.update_id}.mp3"
                logger.info(f"收到音频: {filename}, 大小: {file_size}字节")

            # 3. 语音消息
            elif voice:
                file_size = voice.file_size
                file_type = "语音"
                file_obj = await voice.get_file()
                filename = f"voice_{update.update_id}.ogg"
                logger.info(f"收到语音: {filename}, 大小: {file_size}字节")

            # 4. 图片处理
            elif photo:
                photo_sizes = photo
                largest_photo = photo_sizes[-1]
                file_size = largest_photo.file_size
                file_type = "图片"
                filename = f"photo_{update.update_id}.jpg"
                file_obj = await largest_photo.get_file()
                logger.info(f"收到图片: {filename}, 大小: {file_size}字节")

            # 5. 普通文件处理
            elif document:
                filename = document.file_name
                file_size = document.file_size
                file_obj = await document.get_file()
                # 判断文件类型
                ext = Path(filename).suffix.lower()
                if ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']:
                    file_type = "文档"
                elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz']:
                    file_type = "压缩包"
                elif ext in ['.exe', '.msi']:
                    file_type = "程序"
                else:
                    file_type = "文件"
                logger.info(f"收到{file_type}: {filename}, 大小: {file_size}字节")

            else:
                await update.message.reply_text("[错误] 未检测到文件")
                return

            # 检查文件大小
            max_size = 100 * 1024 * 1024  # 100MB (视频/音频可以更大)
            if file_size > max_size:
                await update.message.reply_text(
                    f"[错误] 文件过大: {file_size/(1024*1024):.1f}MB (最大100MB)"
                )
                return

            # 通知用户
            size_str = f"{file_size/1024:.1f}KB" if file_size < 1024*1024 else f"{file_size/(1024*1024):.1f}MB"
            await update.message.reply_text(
                f"[接收{file_type}] 正在保存: {filename} ({size_str})..."
            )

            # 确定保存路径
            desktop = Path.home() / 'Desktop'
            save_path = desktop / filename

            # 下载文件（带重试机制）
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    logger.info(f"开始下载文件 (尝试 {attempt + 1}/{max_retries}): {filename}")
                    await file_obj.download_to_drive(save_path)
                    break  # 下载成功，退出重试循环
                except Exception as download_error:
                    if attempt < max_retries - 1:
                        logger.warning(f"下载失败，重试中... ({attempt + 1}/{max_retries}): {download_error}")
                        await asyncio.sleep(2)  # 等待2秒后重试
                    else:
                        raise download_error

            # 确认文件已保存
            actual_size = os.path.getsize(save_path)
            actual_size_str = f"{actual_size/1024:.1f}KB" if actual_size < 1024*1024 else f"{actual_size/(1024*1024):.1f}MB"

            # 根据文件类型显示不同信息
            type_emoji = {
                "视频": "🎬",
                "音频": "🎵",
                "语音": "🎤",
                "图片": "🖼️",
                "文档": "📄",
                "压缩包": "📦",
                "程序": "💾",
                "文件": "📎"
            }

            emoji = type_emoji.get(file_type, "📎")

            await update.message.reply_text(
                f"[OK] {emoji}{file_type}已保存\n\n"
                f"文件名: {filename}\n"
                f"类型: {file_type}\n"
                f"路径: {save_path}\n"
                f"大小: {actual_size_str}"
            )

            logger.info(f"{file_type}已保存: {save_path}")

        except Exception as e:
            logger.error(f"处理文件失败: {e}")
            import traceback
            traceback.print_exc()
            await update.message.reply_text(f"[错误] 处理失败: {str(e)[:100]}")

    def run(self):
        bot_token = self.config['bot_token']

        # 配置连接超时和重试设置
        application = (
            Application.builder()
            .token(bot_token)
            .connect_timeout(30.0)  # 连接超时30秒
            .pool_timeout(30.0)  # 连接池超时30秒
            .read_timeout(300.0)  # 读取超时5分钟（大文件下载）
            .write_timeout(30.0)  # 写入超时30秒
            .build()
        )

        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_cmd))
        # 按钮回调处理器
        application.add_handler(CallbackQueryHandler(self.button_callback))
        # 文件处理器（按优先级）
        application.add_handler(MessageHandler(filters.VIDEO & ~filters.COMMAND, self.handle_document))
        application.add_handler(MessageHandler(filters.AUDIO & ~filters.COMMAND, self.handle_document))
        application.add_handler(MessageHandler(filters.VOICE & ~filters.COMMAND, self.handle_document))
        application.add_handler(MessageHandler(filters.PHOTO & ~filters.COMMAND, self.handle_document))
        application.add_handler(MessageHandler(filters.Document.ALL & ~filters.COMMAND, self.handle_document))
        # 文本消息处理器
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        logger.info("Bot started (Forward mode)")
        logger.info(f"请求目录: {self.request_dir}")
        logger.info(f"响应目录: {self.response_dir}")
        application.run_polling()


import asyncio

def main():
    print("=" * 60)
    print("  Claude Code转发Bot")
    print("  直接转发消息给Claude Code")
    print("=" * 60)

    bot = ForwardBot()
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\nBot stopped")

if __name__ == '__main__':
    main()
