import discord
from discord import app_commands
from discord.ext import tasks, commands
import datetime
import os
import asyncio
from typing import List, Dict

# インテントの設定
intents = discord.Intents.default()
intents.members = True
intents.message_content = True  # メッセージ内容の取得を許可

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.reminders: List[Dict] = []

    async def setup_hook(self):
        # スラッシュコマンドの同期（これを行わないとコマンドが表示されません）
        await self.tree.sync()
        # リマインダーチェックタスクの開始
        self.check_reminders.start()

    @tasks.loop(seconds=60)
    async def check_reminders(self):
        # 日本時間(JST)を取得（UTC+9時間）
        jst = datetime.timezone(datetime.timedelta(hours=9))
        now = datetime.datetime.now(jst)
        current_time = now.strftime("%H:%M")
        
        print(f"現在時刻(JST): {current_time}") # ログで確認用
        
        to_remove = []
        for reminder in self.reminders:
            if reminder["time"] == current_time:
                channel = self.get_channel(reminder["channel_id"])
                if channel:
                    user = await self.fetch_user(reminder["user_id"])
                    await channel.send(f"{user.mention} {reminder['message']}")
                    # 送信後にリストから削除
                    to_remove.append(reminder)
        
        for r in to_remove:
            self.reminders.remove(r)

    @check_reminders.before_loop
    async def before_check_reminders(self):
        await self.wait_until_ready()

bot = MyBot()

@bot.tree.command(name="remind", description="指定した時間にメンションとメッセージを送ります")
@app_commands.describe(
    time="時間を指定してください (例: 08:30)",
    message="送りたい一言を入力してください",
    user="メンションしたいユーザーを選択してください（未指定なら自分）"
)
async def remind(interaction: discord.Interaction, time: str, message: str, user: discord.Member = None):
    # 時刻フォーマットのバリデーション
    try:
        datetime.datetime.strptime(time, "%H:%M")
    except ValueError:
        await interaction.response.send_message("時間の形式が正しくありません。HH:MM形式（例: 09:00）で入力してください。", ephemeral=True)
        return

    target_user = user if user else interaction.user
    
    bot.reminders.append({
        "time": time,
        "message": message,
        "user_id": target_user.id,
        "channel_id": interaction.channel_id
    })
    
    await interaction.response.send_message(f"{time}に{target_user.display_name}さんへ「{message}」とリマインドします！", ephemeral=True)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if token:
        bot.run(token)
    else:
        print("Error: DISCORD_TOKEN environment variable is not set.")
