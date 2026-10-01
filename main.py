import os, re, time, threading, asyncio, socket, io, random, json
from collections import defaultdict, deque
from datetime import datetime, timedelta
from flask import Flask
import discord
from discord.ext import commands, tasks
import aiohttp
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

print("="*60)
print("ULTIMATE 4in1 STARTING...")
print("="*60)

# ========== CONFIG ==========
LOG_ID = 1554603044296200342
ADMIN_ROLES = [1538683760080322660, 1538683649682313306, 1538591967368323162, 1537833274875838515]
AUTO_TIMEOUT_ROOM_ID = 1554592139587878912
WELCOME_CHANNEL_ID = 1537832797538885654
GOODBYE_CHANNEL_ID = 1554925370615136367
AUTO_ROLE_ID = 1538952095829458974
YT_ROOM_ID = 1539658526929195018
YT_ROLE_ID = 1539658913006227506
ACCEPT_ROLE_ID = 1554188748479271065
COMMAND_ROOM_ID = 1553859013534552084
APPY_LOG_ROOM_ID = 1553859013534552084
YT_HANDLES = ["@abo_khrbaa","@id7o212","@seagull1x","@ABO8ALY","@bani_drb7h","@imonkey_d"]

TOKEN = os.getenv("TOKEN") or os.getenv("DISCORD_TOKEN") or os.getenv("BOT_TOKEN") or os.getenv("DISCORD_BOT_TOKEN")

if TOKEN:
    print(f"✅ TOKEN FOUND - Length: {len(TOKEN)} - Starts: {TOKEN[:10]}...")
else:
    print("❌ NO TOKEN FOUND! Available env vars:")
    print([k for k in os.environ.keys() if "TOKEN" in k.upper() or "DISCORD" in k.upper()])

# Flask
app = Flask('')
@app.route('/')
def home(): 
    return "ULTIMATE 4in1 ALIVE - Bot should be online in Discord"
threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080), daemon=True).start()
print("✅ Flask started on port 8080")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

msg_cache = defaultdict(lambda: deque(maxlen=20))
ban_cache = defaultdict(list)

def is_admin(m):
    if not m: return False
    if m.guild_permissions.administrator: return True
    return any(r.id in ADMIN_ROLES for r in m.roles)

def is_whitelisted(m):
    if not m: return False
    return False

async def get_audit(guild, action):
    try:
        async for entry in guild.audit_logs(limit=1, action=action):
            if (datetime.now().astimezone() - entry.created_at).total_seconds() < 10:
                return entry.user
    except: pass
    return None

async def punish(guild, user, reason_ar, reason_en, level=1):
    try:
        member = guild.get_member(user.id) if isinstance(user, discord.User) else user
        if not member: return
        if is_admin(member) and level >=3: return
        log = guild.get_channel(LOG_ID)
        if level==1:
            await member.timeout(discord.utils.utcnow() + timedelta(hours=2), reason=reason_en)
            act="timeout"
        elif level==2:
            await member.kick(reason=reason_en)
            act="kick"
        else:
            await guild.ban(member, reason=reason_en, delete_message_days=1)
            act="ban"
        if log:
            e=discord.Embed(title="🛡️ حماية", description=f"{member.mention} {reason_ar} -> {act}", color=0xff0000)
            await log.send(embed=e)
    except Exception as ex:
        print(f"punish err {ex}")

# Questions
QUESTIONS_FILE = "questions.json"
def load_q():
    if not os.path.exists(QUESTIONS_FILE): return []
    try:
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return []
def save_q(qs):
    with open(QUESTIONS_FILE, "w", encoding="utf-8") as f: json.dump(qs, f, ensure_ascii=False, indent=2)

# YouTube - FIXED CLOSED SESSIONS
YT_CHANNELS = {}
YT_LAST = {}

async def get_cid(handle):
    print(f"Resolving YT {handle}...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://www.youtube.com/{handle}", headers={"User-Agent":"Mozilla/5.0"}, timeout=10) as resp:
                txt = await resp.text()
                m = re.search(r'"channelId":"(UC[^"]+)"', txt)
                if m: 
                    print(f"✅ {handle} -> {m.group(1)}")
                    return m.group(1)
    except Exception as e:
        print(f"YT resolve error {handle}: {e}")
    return None

@tasks.loop(seconds=90)
async def yt_check():
    await bot.wait_until_ready()
    if not YT_CHANNELS: return
    try:
        async with aiohttp.ClientSession() as session:
            for cid, name in list(YT_CHANNELS.items()):
                try:
                    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}"
                    async with session.get(url, timeout=10) as resp:
                        if resp.status != 200: continue
                        txt = await resp.text()
                        root = ET.fromstring(txt)
                        ns = {'atom':'http://www.w3.org/2005/Atom','yt':'http://www.youtube.com/xml/schemas/2015'}
                        entry = root.find('atom:entry', ns)
                        if not entry: continue
                        vid = entry.find('yt:videoId', ns).text
                        title = entry.find('atom:title', ns).text
                        link = entry.find('atom:link', ns).attrib['href']
                        if cid not in YT_LAST:
                            YT_LAST[cid] = vid
                            continue
                        if YT_LAST[cid] != vid:
                            YT_LAST[cid] = vid
                            ch = bot.get_channel(YT_ROOM_ID)
                            if ch:
                                em = discord.Embed(title=title, url=link, description=f"جديد من {name}", color=0xFF0000)
                                em.set_image(url=f"https://img.youtube.com/vi/{vid}/maxresdefault.jpg")
                                await ch.send(content=f"<@&{YT_ROLE_ID}>", embed=em)
                                print(f"YT posted {title}")
                except Exception as e:
                    print(f"YT check error {e}")
    except Exception as e:
        print(f"YT loop error {e}")

async def create_welcome_image(member):
    try:
        img = Image.new('RGB', (1000, 400), (15,15,15))
        draw = ImageDraw.Draw(img)
        draw.rectangle([(5,5), (995, 395)], outline=(255,70,0), width=4)
        async with aiohttp.ClientSession() as session:
            async with session.get(str(member.display_avatar.url), timeout=10) as resp:
                avatar_bytes = await resp.read()
        avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGB").resize((180,180))
        mask = Image.new('L', (180,180), 0)
        ImageDraw.Draw(mask).ellipse((0,0,180,180), fill=255)
        img.paste(avatar, (50,110), mask)
        draw.text((280,50), "WELCOME", fill=(255,70,0))
        draw.text((280,120), member.name[:20], fill=(255,255,255))
        draw.text((280,190), f"Member #{member.guild.member_count}", fill=(180,180,180))
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return buf
    except Exception as e:
        print(f"welcome img err {e}")
        return None

# Appy Views
class AddModal(discord.ui.Modal, title="Set Questions"):
    q_input = discord.ui.TextInput(label="كل سؤال بسطر", style=discord.TextStyle.paragraph, required=True)
    async def on_submit(self, interaction: discord.Interaction):
        qs = [q.strip() for q in self.q_input.value.split("\n") if q.strip()]
        save_q(qs)
        await interaction.response.send_message(f"تم حفظ {len(qs)} اسئلة", ephemeral=True)

class PanelView(discord.ui.View):
    def __init__(self): super().__init__(timeout=300)
    @discord.ui.button(label="Set Questions", style=discord.ButtonStyle.blurple)
    async def set_q(self, i, b): await i.response.send_modal(AddModal())
    @discord.ui.button(label="Show", style=discord.ButtonStyle.gray)
    async def show_q(self, i, b):
        qs = load_q()
        txt = "\n".join(qs) if qs else "No questions"
        await i.response.send_message(txt[:1900], ephemeral=True)
    @discord.ui.button(label="Clear", style=discord.ButtonStyle.red)
    async def clear_q(self, i, b):
        save_q([])
        await i.response.send_message("Cleared", ephemeral=True)

class AcceptView(discord.ui.View):
    def __init__(self, mid): super().__init__(timeout=None); self.mid=mid
    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def acc(self, i, b):
        m = i.guild.get_member(self.mid)
        if m:
            role = i.guild.get_role(ACCEPT_ROLE_ID)
            if role:
                try: await m.add_roles(role)
                except: pass
        await i.message.edit(content=f"Accepted <@{self.mid}>", view=None)
        await i.response.send_message("Done", ephemeral=True)
    @discord.ui.button(label="Reject", style=discord.ButtonStyle.red)
    async def rej(self, i, b):
        await i.message.edit(content=f"Rejected <@{self.mid}>", view=None)
        await i.response.send_message("Done", ephemeral=True)

@bot.event
async def on_ready():
    print("="*60)
    print(f"✅✅✅ BOT READY: {bot.user} ID: {bot.user.id}")
    print(f"✅ In {len(bot.guilds)} guilds")
    print("="*60)
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"Sync error {e}")
    # Resolve YT after ready
    for h in YT_HANDLES:
        cid = await get_cid(h)
        if cid: YT_CHANNELS[cid]=h
    if not yt_check.is_running():
        yt_check.start()
        print("✅ YT checker started")

@bot.event
async def on_member_join(member):
    if AUTO_ROLE_ID:
        try:
            r = member.guild.get_role(AUTO_ROLE_ID)
            if r: await member.add_roles(r)
        except Exception as e: print(f"Auto role err {e}")
    ch = member.guild.get_channel(WELCOME_CHANNEL_ID)
    if not ch: return
    buf = await create_welcome_image(member)
    em = discord.Embed(title=f"Welcome {member.guild.name}", description=f"اهلا {member.mention}", color=0xFF4600)
    if buf:
        await ch.send(content=member.mention, embed=em, file=discord.File(buf, filename="welcome.png"))
    else:
        await ch.send(content=member.mention, embed=em)

@bot.event
async def on_member_remove(member):
    ch = member.guild.get_channel(GOODBYE_CHANNEL_ID)
    if ch: await ch.send(f"{member.name} طلع 👋")

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild: return
    if message.channel.id == AUTO_TIMEOUT_ROOM_ID and not is_admin(message.author):
        try:
            await message.delete()
            await message.author.timeout(discord.utils.utcnow() + timedelta(hours=1), reason="ممنوع")
        except: pass
        return
    # anti spam
    now = time.time()
    msg_cache[message.author.id].append(now)
    recent = [t for t in msg_cache[message.author.id] if now - t < 5]
    if len(recent) >=5 and not is_admin(message.author):
        try:
            await message.delete()
            await message.author.timeout(discord.utils.utcnow() + timedelta(hours=1), reason="سبام")
        except: pass
        return
    await bot.process_commands(message)

@bot.tree.command(name="حماية", description="حالة البوت")
async def protection_cmd(interaction: discord.Interaction):
    e=discord.Embed(title="💀 البوت 4 في 1", color=0x000000)
    e.add_field(name="🛡️ حماية", value=f"لوغ: <#{LOG_ID}>", inline=False)
    e.add_field(name="🎥 يوتيوب", value=f"{len(YT_HANDLES)} قنوات", inline=False)
    e.add_field(name="👋 ترحيب", value=f"<#{WELCOME_CHANNEL_ID}>", inline=False)
    await interaction.response.send_message(embed=e, ephemeral=True)

@bot.tree.command(name="تقديم", description="Apply")
async def taqdeem(interaction: discord.Interaction):
    is_ad = any(r.id in ADMIN_ROLES for r in interaction.user.roles) or interaction.user.guild_permissions.administrator
    if is_ad:
        qs = load_q()
        em = discord.Embed(title="لوحة التقديم", description=f"{len(qs)} اسئلة", color=0x8b5cf6)
        return await interaction.response.send_message(embed=em, view=PanelView(), ephemeral=True)
    if interaction.channel.id != COMMAND_ROOM_ID:
        return await interaction.response.send_message(f"استخدم في <#{COMMAND_ROOM_ID}>", ephemeral=True)
    await interaction.response.defer(ephemeral=True)
    qs = load_q()
    if not qs: return await interaction.followup.send("ما في اسئلة", ephemeral=True)
    try: await interaction.user.send(f"تقديمك بدأ {len(qs)} اسئلة")
    except: return await interaction.followup.send("افتح الخاص", ephemeral=True)
    await interaction.followup.send("شيك الخاص", ephemeral=True)
    answers=[]
    def check(m): return m.author.id==interaction.user.id and isinstance(m.channel, discord.DMChannel)
    for q in qs:
        await interaction.user.send(embed=discord.Embed(title=q, color=0x8b5cf6))
        try:
            msg = await bot.wait_for("message", check=check, timeout=300)
            if msg.content.lower() in ["cancel","الغاء"]: await interaction.user.send("الغاء"); return
            answers.append(msg.content)
        except: await interaction.user.send("انتهى الوقت"); return
    ch = bot.get_channel(APPY_LOG_ROOM_ID)
    if ch:
        em = discord.Embed(title="تقديم جديد", description=f"{interaction.user.mention}", color=0x2ecc71)
        for q,a in zip(qs, answers): em.add_field(name=q, value=a[:1024], inline=False)
        await ch.send(embed=em, view=AcceptView(interaction.user.id))
    await interaction.user.send("تم الارسال")

print("Starting bot runner...")

async def runner():
    if not TOKEN:
        print("❌ CRITICAL: NO TOKEN! Add TOKEN env var in Render Dashboard > Environment")
        while True: await asyncio.sleep(60)
    retry=5
    while True:
        try:
            print(f"🚀 Connecting to Discord... retry in {retry}s if fails")
            await bot.start(TOKEN)
        except discord.errors.LoginFailure:
            print("❌ LOGIN FAILURE: Improper token - check TOKEN env var is correct and full")
            await asyncio.sleep(30)
        except Exception as e:
            print(f"⚠️ Bot crashed: {e} - retrying in {retry}s")
            await asyncio.sleep(retry)
            retry = min(retry*1.5, 60)
        else:
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(runner())
                          
