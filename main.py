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
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.reminders: List[Dict] = []

    async def setup_hook(self):
        await self.tree.sync()
        self.check_reminders.start()

    @tasks.loop(seconds=60)
    async def check_reminders(self):
        # ★ここを修正：日本時間を確実に取得
        jst = datetime.timezone(datetime.timedelta(hours=9))
        now = datetime.datetime.now(jst)
        current_time = now.strftime("%H:%M")
        
        # ログに現在時刻を表示（Railwayのログで確認できます）
        print(f"Checking reminders for JST: {current_time}")
        
        to_remove = []
        for reminder in self.reminders:
            if reminder["time"] == current_time:
                channel = self.get_channel(reminder["channel_id"])
                if channel:
                    try:
                        user = await self.fetch_user(reminder["user_id"])
                        await channel.send(f"{user.mention} {reminder['message']}")
                        print(f"Sent message to {user.display_name}")
                        to_remove.append(reminder)
                    except Exception as e:
                        print(f"Error sending message: {e}")
        
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
    
    # ★ここも修正：ボットが認識している現在時刻を返信に含める
    jst = datetime.timezone(datetime.timedelta(hours=9))
    now = datetime.datetime.now(jst)
    await interaction.response.send_message(
        f"了解しました！\n設定時間: {time}\nボットの現在時刻(日本時間): {now.strftime('%H:%M')}\n時間になったら{target_user.display_name}さんへ「{message}」と送ります！", 
        ephemeral=True
    )

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
