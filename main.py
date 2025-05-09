import re
import os
from dotenv import load_dotenv

import discord
from discord.ext import commands

import yt_dlp as youtube_dl

load_dotenv()
TOKEN = os.getenv("TOKEN")
OWNER_ID = os.getenv("OWNER_ID")

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='_', intents=intents, help_command=None)

#Only video, bot doesn't support photos
video_url_patterns = [
    r'https?://(?:www\.)?v\.redd\.it/[a-zA-Z0-9]+',
    r'https?://(?:[^/]+\.)?reddit(?:media)?\.com/r/[^/]+/(?:comments|s)/(?:[a-zA-Z0-9_-]+)+',
    r'https?://clips\.twitch\.tv/[a-zA-Z0-9\-]+',
    r'https?://(?:www\.)?tiktok\.com/(?:embed|@[\w\.-]+/video|t)/\d+',
    r'https?://(?:vm|vt)\.tiktok\.com/\w+',
    r'https?://(?:www\.)?instagram\.com(?:/[^/]+)?/(?:tv|reel)/[^/?#& ]+',
    r'https?://(?:www\.)?youtube\.com/shorts/[a-zA-Z0-9-_]+',
    r'https?://(?:www\.)?pixiv\.net/[a-zA-Z]+/artworks/\d+',
    r'https?://(?:www\.)?furaffinity\.net/view/\d+',
    r'https?://(?:www\.)?twitter\.com/(?:[^/]+/status|statuses)/\d+',
    r'https?://i\.redd\.it/[a-zA-Z0-9]+\.gif',
    r'https?://reddit\.com/r/[a-zA-Z0-9]+/s/[a-zA-Z0-9]+',
    r'https?://(?:www\.)?facebook.com/reel/\d+',
    r'https?://(?:www\.)?facebook.com/watch/\?v=\d+',
    r'https?://(?:www\.)?(?:br\.)?ifunny\.co/video/[a-zA-Z0-9_-]+',
    r'https?://(?:www\.)?(?:old\.)?reddit\.com/gallery/[a-zA-Z0-9]+',
    r'https?://danbooru\.donmai\.us/pools/\d+',
    r'https?://(?:www\.)?tumblr\.com/[a-zA-Z0-9-]+/\d+/[a-zA-Z0-9-]+',
    r'https?://(?:www\.)?[a-zA-Z0-9-]+\.tumblr\.com/post/\d+/[a-zA-Z0-9-]+'
]

video_url_regex = re.compile('|'.join(video_url_patterns))

ydl_opts = {
    'format': 'best',
    'outtmpl': '%(id)s.%(ext)s',
    'cookiefile': 'cookies.txt', 
}

@bot.event
async def on_ready():
    print(f'Bot {bot.user} is ready!')
    try:
        sync = await bot.tree.sync()
        print(f'Sync {len(sync)} command(s)')
    except Exception as e:
        print(e)

@bot.event
async def on_message(message):
    if message.author.bot:
        return 

    if message.author == bot.user:
        return

    if re.search(r'\.\s*https?://', message.content):
        return

    video_urls = video_url_regex.findall(message.content)
    video_urls = [''.join(filter(None, url)) for url in video_urls if ''.join(filter(None, url))]

    if not video_urls:
        return

    print(f'Extracted video URLs: {video_urls}')

    async with message.channel.typing():
        for url in video_urls:
            try:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    result = ydl.extract_info(url, download=True)
                    if 'entries' in result:
                        result = result['entries'][0]
                    video_title = result.get('title', 'Video')
                    video_file = ydl.prepare_filename(result)
                    
                    
                    
                    class OriginalLinkButton(discord.ui.View):
                        def __init__(self, url):
                            super().__init__()
                            self.add_item(discord.ui.Button(label='Original Link', url=url))
                    
                    view = OriginalLinkButton(url)
                    await message.reply(f"**Video được gửi từ: {message.author.mention}**\n{video_title}\n", file=discord.File(video_file), view=view, allowed_mentions = discord.AllowedMentions.none())
                    os.remove(video_file)

            except Exception as e:
                await message.reply(f'Error: {str(e)}')
        
        await message.delete()

@bot.tree.command(name='help', description='Bạn cần trợ giúp?')
async def help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Help",
        description=f"Chào mừng bạn đến với **{interaction.client.user.display_name}** - trợ thủ đắc lực của bạn trong việc quản lý và hiển thị lại các liên kết video một cách chuyên nghiệp và tiện lợi trên Discord!",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="Tính Năng Nổi Bật:",
        value=f"1. Phát Hiện Liên Kết:\n`-Bot có khả năng tự động phát hiện các liên kết video được gửi trong tin nhắn của người dùng.\n- Hỗ trợ nhiều nền tảng video phổ biến như YouTube, TikTok, Instagram, Twitch, Reddit, và nhiều hơn nữa.`\n2. Re-Embed Liên Kết:\n`- Sau khi phát hiện, bot sẽ tải và nhúng lại liên kết video đó với thông tin chi tiết như tiêu đề và mô tả.\n- Cung cấp trải nghiệm xem video mượt mà và tiện lợi ngay trong Discord.`\n3. Các câu lệnh khả dụng\n`/help : Bạn cần trợ giúp?\n/information : Hiển thị thông tin về bot\n/show_patterns : Hiển thị các regex link của bot`\n\nBot đang trong quá trình thử nghiệm, nếu có lỗi hoặc thắc mắc, hãy thông báo cho admin qua Discord <@{OWNER_ID}>",
        inline=False
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='show_patterns', description='Hiển thị các regex link của bot')
async def show_patterns(interaction: discord.Interaction):
    patterns_description = "\n".join([f'```{pattern}```' for pattern in video_url_patterns])
    embed = discord.Embed(
        title="Regex Patterns",
        description=patterns_description,
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='information', description='Thông tin về bot')
async def information(interaction: discord.Interaction):
    embed = discord.Embed(
        title="INFORMATION",
        description=f"**Tên:** {interaction.client.user.display_name}\n**Owner:** <@{OWNER_ID}>\n**Ngôn ngữ lập trình:** Python\n**Hỗ trợ:** TikTok, Instagram, Reddit, Twitter/X, Youtube Shorts, Facebook \n**OFFICIAL WEBSITE:** [teochanchan.site](https://teochanchan.site)\n\nBot là trợ thủ đắc lực của bạn trong việc quản lý và hiển thị lại các liên kết video một cách chuyên nghiệp và tiện lợi trên Discord!",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=f'{interaction.client.user.avatar}')
    await interaction.response.send_message(embed=embed)


bot.run(TOKEN)