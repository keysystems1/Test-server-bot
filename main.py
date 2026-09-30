# ULTIMATE 4in1 - Protection + YouTube + Welcome + Appy 🔥
# كل البوتات في بوت واحد اسطوري
import os, re, time, threading, asyncio, socket, io, random, json
from collections import defaultdict, deque
from datetime import datetime, timedelta
from flask import Flask
import discord
from discord.ext import commands, tasks
from discord import app_commands
import aiohttp
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

# ========== CONFIG - PROTECTION ==========
LOG_ID = 1554603044296200342
ADMIN_ROLES = [1538683760080322660, 1538683649682313306, 1538591967368323162, 1537833274875838515]
OWNER_ID = 0
WHITELIST_USERS = set()
WHITELIST_DOMAINS = ["discord.com", "youtube.com", "youtu.be", "tenor.com", "giphy.com", "imgur.com"]
AUTO_TIMEOUT_ROOM_ID = 1554592139587878912
AUTO_TIMEOUT_SECONDS = 60 * 60
AUTO_TIMEOUT_REASON = "ممنوع الكتابة في هذا الروم"
SCAM_DOMAINS = ["lacewin.com","discord.gift","nitro.gift","free-nitro","discord-nitro","steamcommunity.com/login","steam-nitro","crypto-bonus","bitex","airdrop","claim-airdrop","giveaway-crypto","mrbeast.bonus","mrbeast-casino","beast-games-bonus","discord-app.com","discordu.com"]
SCAM_REGEX = [r"withdrawal of \$\d+.*was successful",r"withdrawal success",r"your withdrawal of \$\d+",r"\$2500.*bonus",r"\$2700.*successful",r"activate code for bonus",r"special promocode",r"i am pleased to announce.*casino",r"giving away \$\d+.*everyone who registers",r"bonus.*play or withdraw",r"received.*\+.*usdt",r"free discord nitro.*click",r"http.*discord.*nitro.*free"]
INVITE_REGEX = re.compile(r"(discord\.gg/|discord\.com/invite/|discordapp\.com/invite/)\w+")
EVERYONE_REGEX = re.compile(r"@everyone|@here")

# ========== CONFIG - YOUTUBE ==========
YT_ROOM_ID = 1539658526929195018
YT_ROLE_ID = 1539658913006227506
CHANNEL_HANDLES = ["@abo_khrbaa","@id7o212","@seagull1x","@ABO8ALY","@bani_drb7h","@imonkey_d"]
YT_CHANNELS = {}
YT_LAST = {}

# ========== CONFIG - WELCOME ==========
WELCOME_CHANNEL_ID = 1537832797538885654
GOODBYE_CHANNEL_ID = 1554925370615136367
AUTO_ROLE_ID = 1538952095829458974
WELCOME_MESSAGES = [
    "يا هلا والله نورت السيرفر يا {mention} 🔥",
    "ارحبووووو وصل {name} الأسطورة 👑",
    "يا مرحبا يا {name} - السيرفر نور بوجودك ✨",
    "حي الله {mention} - مكانك محفوظ من زمان 💀",
    "اهلا اهلا {name} - توقعنا وصولك 😎",
]

# ========== CONFIG - APPY ==========
ACCEPT_ROLE_ID = 1554188748479271065
COMMAND_ROOM_ID = 1553859013534552084
APPY_LOG_ROOM_ID = 1553859013534552084
QUESTIONS_FILE = "questions.json"

def load_q():
    if not os.path.exists(QUESTIONS_FILE):
        return []
    try:
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_q(qs):
    with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(qs, f, ensure_ascii=False, indent=2)

# ========== FLASK ==========
app = Flask('')
@app.route('/')
def home(): return "ULTIMATE 4in1 - Protection + YouTube + Welcome + Appy ALIVE 🔥"
threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080), daemon=True).start()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

msg_cache = defaultdict(lambda: deque(maxlen=20))
join_cache = deque(maxlen=30)
ban_cache = defaultdict(list)
is_raid_mode = False

def is_admin(m):
    if not m: return False
    if m.guild_permissions.administrator: return True
    return any(r.id in ADMIN_ROLES for r in m.roles)

def is_whitelisted(m):
    if not m: return False
    if m.id in WHITELIST_USERS: return True
    if m.id == OWNER_ID: return True
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
        if is_whitelisted(user): return
        member = guild.get_member(user.id) if isinstance(user, discord.User) else user
        if not member: return
        if is_admin(member) and level >=3: return
        log = guild.get_channel(LOG_ID)
        if level==1:
            await member.timeout(discord.utils.utcnow() + timedelta(hours=2), reason=reason_en)
            act_ar="تايم اوت ساعتين ⏰"
        elif level==2:
            await member.kick(reason=reason_en)
            act_ar="طرد 👢"
        else:
            await guild.ban(member, reason=reason_en, delete_message_days=1)
            act_ar="بان نهائي 🔨"
        if log:
            e=discord.Embed(title="🛡️ نظام الحماية", color=0xff0000, timestamp=datetime.now())
            e.add_field(name="👤 العضو", value=f"{member.mention}\n`{member.id}`", inline=False)
            e.add_field(name="📝 السبب", value=reason_ar, inline=False)
            e.add_field(name="⚖️ العقوبة", value=act_ar, inline=True)
            await log.send(embed=e)
    except Exception as ex:
        print(f"punish err {ex}")

# ========== WELCOME IMAGE ==========
async def create_welcome_image(member):
    try:
        width, height = 1000, 400
        img = Image.new('RGB', (width, height), color=(15, 15, 15))
        draw = ImageDraw.Draw(img)
        draw.rectangle([(5,5), (width-5, height-5)], outline=(255, 70, 0), width=4)
        async with aiohttp.ClientSession() as session:
            async with session.get(str(member.display_avatar.url)) as resp:
                avatar_bytes = await resp.read()
        avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGB").resize((180, 180))
        mask = Image.new('L', (180, 180), 0)
        ImageDraw.Draw(mask).ellipse((0,0,180,180), fill=255)
        img.paste(avatar, (50, 110), mask)
        try:
            font_big = ImageFont.truetype("arial.ttf", 50)
            font_small = ImageFont.truetype("arial.ttf", 28)
        except:
            font_big = ImageFont.load_default()
            font_small = ImageFont.load_default()
        draw.text((280, 50), "WELCOME", fill=(255, 70, 0), font=font_big)
        draw.text((280, 120), member.name[:20], fill=(255, 255, 255), font=font_big)
        draw.text((280, 190), f"Member #{member.guild.member_count}", fill=(180,180,180), font=font_small)
        draw.text((280, 240), random.choice(WELCOME_MESSAGES).format(mention=member.mention, name=member.name)[:40], fill=(255,255,255), font=font_small)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return buf
    except Exception as e:
        print(f"welcome img err {e}")
        return None

# ========== YOUTUBE ==========
async def get_cid(handle):
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(f"https://www.youtube.com/{handle}", headers={"User-Agent":"Mozilla/5.0"}) as r:
                txt = await r.text()
                m = re.search(r'"channelId":"(UC[^"]+)"', txt)
                if m: return m.group(1)
    except: pass
    return None

@tasks.loop(seconds=90)
async def yt_check():
    await bot.wait_until_ready()
    async with aiohttp.ClientSession() as s:
        for cid, name in YT_CHANNELS.items():
            try:
                url = f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}"
                async with s.get(url) as r:
                    if r.status!= 200: continue
                    txt = await r.text()
                    root = ET.fromstring(txt)
                    ns = {'atom':'http://www.w3.org/2005/Atom','yt':'http://www.youtube.com/xml/schemas/2015'}
                    e = root.find('atom:entry', ns)
                    if not e: continue
                    vid = e.find('yt:videoId', ns).text
                    title = e.find('atom:title', ns).text
                    link = e.find('atom:link', ns).attrib['href']
                    if cid not in YT_LAST:
                        YT_LAST[cid] = vid
                        continue
                    if YT_LAST[cid]!= vid:
                        YT_LAST[cid] = vid
                        ch = bot.get_channel(YT_ROOM_ID)
                        if ch:
                            em = discord.Embed(title=title, url=link, description=f"جديد من {name}", color=0xFF0000)
                            em.set_image(url=f"https://img.youtube.com/vi/{vid}/maxresdefault.jpg")
                            await ch.send(content=f"<@&{YT_ROLE_ID}>", embed=em)
            except Exception as e:
                print(f"YT error {e}")

# ========== APPY VIEWS ==========
class AddModal(discord.ui.Modal, title="Set Questions"):
    q_input = discord.ui.TextInput(label="كل سؤال بسطر", style=discord.TextStyle.paragraph, required=True)
    async def on_submit(self, interaction: discord.Interaction):
        qs = [q.strip() for q in self.q_input.value.split("\n") if q.strip()]
        save_q(qs)
        await interaction.response.send_message(f"تم حفظ {len(qs)} اسئلة", ephemeral=True)

class PanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    @discord.ui.button(label="Set Questions", style=discord.ButtonStyle.blurple)
    async def set_q(self, i, b):
        await i.response.send_modal(AddModal())
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
    def __init__(self, mid):
        super().__init__(timeout=None)
        self.mid = mid
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
    print(f"BOT READY {bot.user} in {len(bot.guilds)} guilds")
    try:
        await bot.tree.sync()
        print("Slash synced")
    except Exception as e:
        print(f"Sync error {e}")
    for h in CHANNEL_HANDLES:
        cid = await get_cid(h)
        if cid:
            YT_CHANNELS[cid] = h
            print(f"YT mapped {h} -> {cid}")
    if not yt_check.is_running():
        yt_check.start()

@bot.event
async def on_member_join(member):
    if AUTO_ROLE_ID:
        try:
            r = member.guild.get_role(AUTO_ROLE_ID)
            if r: await member.add_roles(r)
        except: pass
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
    if ch:
        await ch.send(f"{member.name} طلع - باي باي 👋")

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild: return
    guild = message.guild
    low = message.content.lower()
    if message.channel.id == AUTO_TIMEOUT_ROOM_ID and not is_admin(message.author):
        try:
            await message.delete()
            await message.author.timeout(discord.utils.utcnow() + timedelta(seconds=AUTO_TIMEOUT_SECONDS), reason=AUTO_TIMEOUT_REASON)
            log = guild.get_channel(LOG_ID)
            if log:
                await log.send(f"⏰ {message.author.mention} كتب في <#{AUTO_TIMEOUT_ROOM_ID}> - تايم اوت ساعة")
        except: pass
        return
    for d in SCAM_DOMAINS:
        if d in low:
            try: await message.delete()
            except: pass
            await punish(guild, message.author, f"سكام {d}", f"Scam {d}", 3)
            return
    for pat in SCAM_REGEX:
        if re.search(pat, low):
            try: await message.delete()
            except: pass
            await punish(guild, message.author, f"سكام", f"Scam pattern", 3)
            return
    if INVITE_REGEX.search(message.content):
        is_whitelisted_link = any(dom in low for dom in WHITELIST_DOMAINS)
        if not is_whitelisted_link:
            try: await message.delete()
            except: pass
            await punish(guild, message.author, "دعوات", "Invite", 1)
            return
    if EVERYONE_REGEX.search(message.content) and "http" in low:
        try: await message.delete()
        except: pass
        await punish(guild, message.author, "@everyone + رابط", "Hacked", 3)
        return
    if len(message.mentions)>5:
        try: await message.delete()
        except: pass
        await punish(guild, message.author, f"منشن {len(message.mentions)}", "Mass", 1)
        return
    uid=message.author.id
    now=time.time()
    msg_cache[uid].append(now)
    recent=[t for t in msg_cache[uid] if now-t<5]
    if len(recent)>=5:
        try: await message.delete()
        except: pass
        await punish(guild, message.author, f"سبام {len(recent)}", "Spam", 1)
        msg_cache[uid].clear()
        return
    if len(message.attachments)>3:
        try: await message.delete()
        except: pass
        await punish(guild, message.author, "سبام صور", "Image spam", 1)
        return
    await bot.process_commands(message)

@bot.event
async def on_guild_channel_delete(channel):
    ex=await get_audit(channel.guild, discord.AuditLogAction.channel_delete)
    if ex and not is_whitelisted(ex) and not is_admin(ex):
        await punish(channel.guild, ex, f"حذف روم {channel.name}", f"Del {channel.name}", 3)

@bot.event
async def on_guild_role_delete(role):
    ex=await get_audit(role.guild, discord.AuditLogAction.role_delete)
    if ex and not is_whitelisted(ex) and not is_admin(ex):
        await punish(role.guild, ex, f"حذف رتبة {role.name}", f"Del role {role.name}", 3)

@bot.event
async def on_member_ban(guild, user):
    ban_cache[guild.id].append(time.time())
    recent=[t for t in ban_cache[guild.id] if time.time()-t<10]
    if len(recent)>=3:
        ex=await get_audit(guild, discord.AuditLogAction.ban)
        if ex and not is_whitelisted(ex) and not is_admin(ex):
            await punish(guild, ex, f"بان جماعي {len(recent)}", f"Mass ban", 3)
            ban_cache[guild.id].clear()

@bot.event
async def on_webhooks_update(channel):
    ex=await get_audit(channel.guild, discord.AuditLogAction.webhook_create)
    if ex and not is_whitelisted(ex) and not is_admin(ex):
        try:
            whs=await channel.webhooks()
            for wh in whs: await wh.delete(reason="Anti webhook")
            await punish(channel.guild, ex, "ويبهوك", "Webhook", 2)
        except: pass

# ========== COMMANDS ==========
@bot.tree.command(name="حماية", description="حالة البوت الشامل")
async def protection_cmd(interaction: discord.Interaction):
    e=discord.Embed(title="💀 البوت الشامل 4 في 1 - الأسطوري", color=0x000000)
    e.add_field(name="🛡️ الحماية", value=f"اللوغ: <#{LOG_ID}>\nتايم اوت: <#{AUTO_TIMEOUT_ROOM_ID}>", inline=False)
    e.add_field(name="🎥 يوتيوب", value=f"{len(CHANNEL_HANDLES)} قنوات - <#{YT_ROOM_ID}> - <@&{YT_ROLE_ID}>\n" + "\n".join(CHANNEL_HANDLES), inline=False)
    e.add_field(name="👋 ترحيب", value=f"ترحيب: <#{WELCOME_CHANNEL_ID}>\nمغادرة: <#{GOODBYE_CHANNEL_ID}>\nرول: <@&{AUTO_ROLE_ID}>", inline=False)
    e.add_field(name="📝 تقديم Appy", value=f"روم التقديم: <#{COMMAND_ROOM_ID}>\nلوغ التقديم: <#{APPY_LOG_ROOM_ID}>\nرول القبول: <@&{ACCEPT_ROLE_ID}>\nاستخدم /تقديم", inline=False)
    await interaction.response.send_message(embed=e, ephemeral=True)

@bot.tree.command(name="تقديم", description="Apply or Setup Panel for Admins")
async def taqdeem(interaction: discord.Interaction):
    is_admin_user = any(r.id in ADMIN_ROLES for r in interaction.user.roles) or interaction.user.guild_permissions.administrator
    if is_admin_user:
        qs = load_q()
        embed = discord.Embed(title="Appy Control Panel", description=f"انت ادمن - هنا تحط اسئلة التقديم\n\nالحالي: {len(qs)} سؤال\nروم التقديم: <#{COMMAND_ROOM_ID}>", color=0x8b5cf6)
        return await interaction.response.send_message(embed=embed, view=PanelView(), ephemeral=True)
    if interaction.channel.id!= COMMAND_ROOM_ID:
        return await interaction.response.send_message(f"استخدم الامر فقط في <#{COMMAND_ROOM_ID}>", ephemeral=True)
    await interaction.response.defer(ephemeral=True)
    qs = load_q()
    if not qs:
        return await interaction.followup.send("لسا ما في اسئلة - خلي الادمن يحط اسئلة", ephemeral=True)
    try:
        await interaction.user.send(f"هلا! تقديمك في {interaction.guild.name} بدأ - عندك {len(qs)} اسئلة - اكتب cancel للالغاء")
    except:
        return await interaction.followup.send("افتح الخاص DM!", ephemeral=True)
    await interaction.followup.send("شيك الخاص!", ephemeral=True)
    answers=[]
    def check(m): return m.author.id==interaction.user.id and isinstance(m.channel, discord.DMChannel)
    for i,q in enumerate(qs,1):
        await interaction.user.send(embed=discord.Embed(title=f"سؤال {i}/{len(qs)}", description=q, color=0x8b5cf6))
        try:
            msg=await bot.wait_for("message", check=check, timeout=300)
            if msg.content.lower() in ["cancel","الغاء"]:
                await interaction.user.send("تم الالغاء"); return
            answers.append(msg.content)
        except asyncio.TimeoutError:
            await interaction.user.send("انتهى الوقت"); return
    ch=bot.get_channel(APPY_LOG_ROOM_ID)
    if ch:
        embed=discord.Embed(title="📝 تقديم جديد!", description=f"المتقدم: {interaction.user.mention} `{interaction.user.id}`", color=0x2ecc71)
        for q,a in zip(qs, answers):
            embed.add_field(name=q, value=a[:1024], inline=False)
        await ch.send(embed=embed, view=AcceptView(interaction.user.id))
    await interaction.user.send("✅ تم ارسال تقديمك للادارة!")

def get_token(): return os.getenv("TOKEN") or os.getenv("DISCORD_TOKEN") or os.getenv("BOT_TOKEN")
async def check_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except:
        try:
            socket.create_connection(("1.1.1.1", 53), timeout=3)
            return True
        except:
            return False

async def runner():
    token=get_token()
    if not token:
        print("❌ ما لقيت TOKEN")
        return
    retry=5
    while True:
        try:
            while not await check_internet():
                await asyncio.sleep(10)
            print("🚀 يشغل البوت 4in1...")
            await bot.start(token)
        except Exception as e:
            print(f"⚠️ {e}")
            await asyncio.sleep(retry)
            retry=min(retry*1.5, 60)
        else:
            await asyncio.sleep(5)

if __name__=="__main__":
    asyncio.run(runner())
