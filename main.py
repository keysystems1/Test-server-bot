# ULTIMATE 4in1 - Protection + YouTube + Welcome + Appy 🔥
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
    if not os.path.exists(QUESTIONS_FILE): return []
    try:
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return []
def save_q(qs):
    with open(QUESTIONS_FILE, "w", encoding="utf-8") as f: json.dump(qs, f, ensure_ascii=False, indent=2)

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
        draw.text((280, 230), f"Account: {(datetime.now().astimezone() - member.created_at).days} days", fill=(120,120,120), font=font_small)
        draw.text((280, 270), member.guild.name[:35], fill=(255,70,0), font=font_small)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return buf
    except Exception as e:
        print(f"Image error {e}")
        return None

async def get_channel_id(handle):
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(f"https://www.youtube.com/{handle}", headers={"User-Agent": "Mozilla/5.0"}) as r:
                txt = await r.text()
                m = re.search(r'"channelId":"(UC[^"]+)"', txt)
                if m: return m.group(1)
                m = re.search(r'"externalId":"(UC[^"]+)"', txt)
                if m: return m.group(1)
    except Exception as e:
        print(f"YT resolve {handle}: {e}")
    return None

@tasks.loop(seconds=30)
async def youtube_check():
    await bot.wait_until_ready()
    if not YT_CHANNELS: return
    async with aiohttp.ClientSession() as s:
        for cid, name in YT_CHANNELS.items():
            try:
                async with s.get(f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}") as r:
                    if r.status!=200: continue
                    txt = await r.text()
                    root = ET.fromstring(txt)
                    ns = {'atom': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015'}
                    entry = root.find('atom:entry', ns)
                    if not entry: continue
                    vid = entry.find('yt:videoId', ns).text
                    title = entry.find('atom:title', ns).text
                    link = entry.find('atom:link', ns).attrib['href']
                    if cid not in YT_LAST:
                        YT_LAST[cid]=vid
                        continue
                    if YT_LAST[cid]!=vid:
                        YT_LAST[cid]=vid
                        ch = bot.get_channel(YT_ROOM_ID) or await bot.fetch_channel(YT_ROOM_ID)
                        embed = discord.Embed(title=title, url=link, description=f"فيديو جديد من **{name}** 🔥", color=0xFF0000)
                        embed.set_image(url=f"https://img.youtube.com/vi/{vid}/maxresdefault.jpg")
                        embed.set_footer(text=name)
                        await ch.send(content=f"<@&{YT_ROLE_ID}> 🔔 فيديو جديد!", embed=embed)
            except Exception as e:
                print(f"YT Error {name}: {e}")

class AddQuestionModal(discord.ui.Modal, title="Set Application Questions"):
    questions_input = discord.ui.TextInput(label="Put each question on new line", style=discord.TextStyle.paragraph, placeholder="What is your name?\nHow old are you?\nWhy you want staff?", required=True, max_length=2000)
    async def on_submit(self, interaction: discord.Interaction):
        new_qs = [q.strip() for q in self.questions_input.value.split("\n") if q.strip()]
        save_q(new_qs)
        await interaction.response.send_message(f"✅ Saved {len(new_qs)} questions:\n" + "\n".join([f"{i+1}. {q}" for i,q in enumerate(new_qs)]), ephemeral=True)

class PanelView(discord.ui.View):
    def __init__(self): super().__init__(timeout=300)
    @discord.ui.button(label="Set Questions", style=discord.ButtonStyle.blurple)
    async def set_q(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AddQuestionModal())
    @discord.ui.button(label="Show Questions", style=discord.ButtonStyle.gray)
    async def show_q(self, interaction: discord.Interaction, button: discord.ui.Button):
        qs = load_q()
        if not qs: return await interaction.response.send_message("No questions yet", ephemeral=True)
        txt = "\n".join([f"{i+1}. {q}" for i,q in enumerate(qs)])
        await interaction.response.send_message(f"Current ({len(qs)}):\n{txt}", ephemeral=True)
    @discord.ui.button(label="Clear All", style=discord.ButtonStyle.red)
    async def clear_q(self, interaction: discord.Interaction, button: discord.ui.Button):
        save_q([])
        await interaction.response.send_message("Cleared all questions", ephemeral=True)

class AcceptView(discord.ui.View):
    def __init__(self, member_id): super().__init__(timeout=None); self.member_id = member_id
    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not any(r.id in ADMIN_ROLES for r in interaction.user.roles): return await interaction.response.send_message("Only admin", ephemeral=True)
        m = interaction.guild.get_member(self.member_id)
        if m:
            role = interaction.guild.get_role(ACCEPT_ROLE_ID)
            if role:
                try: await m.add_roles(role)
                except: pass
            try: await m.send(f"🎉 You got accepted in {interaction.guild.name}")
            except: pass
        await interaction.message.edit(content=f"✅ Accepted <@{self.member_id}> by {interaction.user.mention}", view=None)
        await interaction.response.send_message("Accepted", ephemeral=True)
    @discord.ui.button(label="Reject", style=discord.ButtonStyle.red)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not any(r.id in ADMIN_ROLES for r in interaction.user.roles): return await interaction.response.send_message("Only admin", ephemeral=True)
        await interaction.message.edit(content=f"❌ Rejected <@{self.member_id}> by {interaction.user.mention}", view=None)
        await interaction.response.send_message("Rejected", ephemeral=True)

@bot.event
async def on_ready():
    print(f"✅ ULTIMATE 4in1 READY {bot.user}")
    try: await bot.tree.sync()
    except: pass
    for handle in CHANNEL_HANDLES:
        cid = await get_channel_id(handle)
        if cid: YT_CHANNELS[cid]=handle
    if not youtube_check.is_running(): youtube_check.start()

@bot.event
async def on_member_join(member):
    global is_raid_mode
    join_cache.append(time.time())
    recent = [t for t in join_cache if time.time()-t<10]
    if len(recent)>=5 and not is_raid_mode:
        is_raid_mode=True
        log = member.guild.get_channel(LOG_ID)
        if log:
            e=discord.Embed(title="🚨 رايد!", color=0xff0000)
            e.add_field(name="التفاصيل", value=f"{len(recent)} دخول ب10 ثواني", inline=False)
            await log.send(embed=e)
        try: await member.guild.edit(verification_level=discord.VerificationLevel.highest)
        except: pass
        await asyncio.sleep(60)
        is_raid_mode=False
        try: await member.guild.edit(verification_level=discord.VerificationLevel.low)
        except: pass
    guild=member.guild
    age_days=(datetime.now().astimezone() - member.created_at).days
    if AUTO_ROLE_ID!=0:
        try:
            role=guild.get_role(AUTO_ROLE_ID)
            if role: await member.add_roles(role, reason="Auto Role")
        except: pass
    if age_days<3:
        log=guild.get_channel(LOG_ID)
        if log:
            e=discord.Embed(title="⚠️ حساب جديد", color=0xffa500, timestamp=datetime.now())
            e.set_thumbnail(url=member.display_avatar.url)
            e.add_field(name="العضو", value=f"{member.mention} `{member.id}`", inline=False)
            e.add_field(name="عمر الحساب", value=f"{age_days} يوم", inline=True)
            await log.send(embed=e)
    channel=guild.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        welcome_text=random.choice(WELCOME_MESSAGES).format(mention=member.mention, name=member.name)
        embed=discord.Embed(title=f"🔥 WELCOME TO {guild.name.upper()} 🔥", description=f"{welcome_text}\n\n👤 **العضو:** {member.mention}\n📊 **رقمك:** #{guild.member_count}\n📅 **عمر حسابك:** {age_days} يوم\n🕒 **دخلت:** <t:{int(datetime.now().timestamp())}:R>\n\nاقرأ القوانين واستمتع 👑", color=0xFF4600, timestamp=datetime.now())
        embed.set_thumbnail(url=member.display_avatar.url)
        img_buf=await create_welcome_image(member)
        try:
            if img_buf:
                file=discord.File(img_buf, filename="welcome.png")
                embed.set_image(url="attachment://welcome.png")
                await channel.send(content=f"{member.mention} {welcome_text}", embed=embed, file=file)
            else:
                await channel.send(content=f"{member.mention} {welcome_text}", embed=embed)
        except Exception as e: print(f"Welcome err {e}")

@bot.event
async def on_member_remove(member):
    channel=member.guild.get_channel(GOODBYE_CHANNEL_ID)
    if not channel: return
    embed=discord.Embed(title="👋 غادر", description=f"**{member.name}** طلع 😢\nكنا {member.guild.member_count+1} صرنا {member.guild.member_count}", color=0x2b2d31, timestamp=datetime.now())
    embed.set_thumbnail(url=member.display_avatar.url)
    await channel.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author.bot: return
    if not message.guild: return
    if is_whitelisted(message.author):
        await bot.process_commands(message)
        return
    if message.channel.id==AUTO_TIMEOUT_ROOM_ID:
        if not is_admin(message.author):
            try: await message.delete()
            except: pass
            try:
                await message.author.timeout(discord.utils.utcnow() + timedelta(seconds=AUTO_TIMEOUT_SECONDS), reason=AUTO_TIMEOUT_REASON)
                await message.channel.send(f"⛔ {message.author.mention} ممنوع الكتابة هنا!", delete_after=5)
            except: pass
            return
    low=message.content.lower()
    guild=message.guild
    for pat in SCAM_REGEX:
        if re.search(pat, low, re.IGNORECASE):
            try: await message.delete()
            except: pass
            await punish(guild, message.author, f"سكام `{pat}`", f"Scam {pat}", 3)
            return
    for d in SCAM_DOMAINS:
        if d in low:
            try: await message.delete()
            except: pass
            await punish(guild, message.author, f"سكام دومين `{d}`", f"Scam {d}", 3)
            return
    if re.search(r"https?://", low) and not any(w in low for w in WHITELIST_DOMAINS):
        age=(datetime.now().astimezone() - message.author.created_at).days
        if age<7:
            try: await message.delete()
            except: pass
            await punish(guild, message.author, f"حساب جديد {age} يوم + رابط", f"New {age}d", 3)
            return
        if INVITE_REGEX.search(low) and not is_admin(message.author):
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

@bot.tree.command(name="حماية", description="حالة البوت الشامل")
async def protection_cmd(interaction: discord.Interaction):
    e=discord.Embed(title="💀 البوت الشامل 4 في 1 - الأسطوري", color=0x000000)
    e.add_field(name="🛡️ الحماية", value=f"اللوغ: <#{LOG_ID}>\nتايم اوت: <#{AUTO_TIMEOUT_ROOM_ID}>", inline=False)
    e.add_field(name="🎥 يوتيوب", value=f"{len(CHANNEL_HANDLES)} قنوات - <#{YT_ROOM_ID}> - <@&{YT_ROLE_ID}>\n" + "\n".join(CHANNEL_HANDLES), inline=False)
    e.add_field(name="👋 ترحيب", value=f"ترحيب: <#{WELCOME_CHANNEL_ID}>\nمغادرة: <#{GOODBYE_CHANNEL_ID}>\nرول: <@&{AUTO_ROLE_ID}>", inline=False)
    e.add_field(name="📝 تقديم Appy", value=f"روم التقديم: <#{COMMAND_ROOM_ID}>\nلوغ التقديم: <#{APPY_LOG_ROOM_ID}>\nرول القبول: <@&{ACCEPT_ROLE_ID}>\nاستخدم /تقدي
