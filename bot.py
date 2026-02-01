import discord
from discord.ext import commands
import asyncio
import os

from flask import Flask
from threading import Thread
import os

# --- 追加: Webサーバーの設定 ---
app = Flask('')

@app.route('/')
def main():
    return "Bot is running!"

def run():
    # Koyebはポート8000を使用するのが一般的です
    app.run(host="0.0.0.0", port=8000)

def keep_alive():
    server = Thread(target=run)
    server.start()
# ----------------------------

# ... (これまでのBotのコード) ...



intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

running_timers = {}

@bot.command()
async def pomodoro(ctx, work_min: int = 25, break_min: int = 5):
    """
    !pomodoro [作業時間] [休憩時間] でタイマーを開始します。
    例: !pomodoro 50 10 (50分作業、10分休憩)
    """
    user_id = ctx.author.id

    if user_id in running_timers and running_timers[user_id] is not None:
        await ctx.send("現在、タイマーが実行中です。中断したい場合は `!stop` を入力してください。")
        return

    # タイマー処理をタスクとして起動
    timer_task = asyncio.create_task(run_custom_timer(ctx, user_id, work_min, break_min))
    running_timers[user_id] = timer_task

async def run_custom_timer(ctx, user_id, work_min, break_min):
    count = 1
    try:
        while True:
            # 開始メッセージ
            await ctx.send(f"🍅 **【{count}セット目】作業開始！** {work_min}分間集中しましょう。")
            await asyncio.sleep(work_min * 60)

            # 休憩開始（@everyoneで通知）
            await ctx.send(f"@everyone ☕ **【{count}セット目】休憩時間！** {break_min}分間休んでください。")
            await asyncio.sleep(break_min * 60)
            
            # 休憩終了（@everyoneで通知）
            await ctx.send(f"@everyone ✅ {count}セット目が完了しました。次のサイクルに入ります！")
            count += 1
            
    except asyncio.CancelledError:
        await ctx.send(f"⏹️ タイマーを終了しました。合計 **{count-1 if count > 1 else 0}セット** 完了！")
    finally:
        running_timers.pop(user_id, None)

@bot.command()
async def stop(ctx):
    """実行中のタイマーを強制終了します"""
    user_id = ctx.author.id
    if user_id in running_timers and running_timers[user_id] is not None:
        running_timers[user_id].cancel()
    else:
        await ctx.send("現在実行中のタイマーはありません。")


from dotenv import load_dotenv
load_dotenv()

# 最後に起動部分を修正
if __name__ == "__main__":
    keep_alive()  # Webサーバーを起動
    bot.run(os.getenv('DISCORD_TOKEN'))


