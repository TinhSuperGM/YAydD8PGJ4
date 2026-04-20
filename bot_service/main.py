import os
import discord
from discord.ext import commands
from api import api_get, api_post

TOKEN = os.getenv("DISCORD_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
PREFIX = ","


def build_profile_embed(data: dict) -> discord.Embed:
    user = data["user"]
    embed = discord.Embed(title="📜 HỒ SƠ TU SĨ", color=discord.Color.gold())
    embed.add_field(name="Tu sĩ", value=f"<@{user.get('id', '')}>", inline=False)
    embed.add_field(name="Nguồn gốc", value=f"**{user['origin_name']}**", inline=False)
    embed.add_field(name="🌟 Linh căn", value=f"**{user['linh_can']}**", inline=True)
    embed.add_field(name="⚔️ Công pháp", value=f"**{user['cong_phap_name']}**", inline=True)
    embed.add_field(name="💠 Cảnh giới", value=f"**{data['realm_text']}**", inline=True)
    embed.add_field(name="🔹 Tiểu cảnh giới", value=f"**{['Sơ Kỳ','Trung Kỳ','Hậu Kỳ','Viên Mãn'][user['minor_stage']]}**", inline=True)
    embed.add_field(name="💎 Linh thạch", value=f"**{user['linh_thach']:,}**", inline=True)
    embed.add_field(name="📈 Chi phí tu luyện kế tiếp", value=f"**{user['minor_cost']:,}** linh thạch", inline=True)
    embed.add_field(name="❤️ HP", value=f"**{user['hp']}**", inline=True)
    embed.add_field(name="🔷 MP", value=f"**{user['mp']}**", inline=True)
    embed.add_field(name="🗡️ ATK", value=f"**{user['atk']}**", inline=True)
    embed.add_field(name="🛡️ DEF", value=f"**{user['defense']}**", inline=True)
    embed.add_field(name="✨ Tu vi", value=f"**{user['tu_vi']}**", inline=True)
    return embed


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)


@bot.event
async def on_ready():
    print(f"Bot đã online: {bot.user}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    await ctx.send(f"❌ Có lỗi xảy ra: `{error}`")


@bot.command(name="start", aliases=["gia-nhap", "gia_nhap", "dangky"])
async def start(ctx, *, origin_input: str = None):
    res = await api_post("/user/start", {
        "user_id": ctx.author.id,
        "name": ctx.author.name,
        "origin_input": origin_input,
    })

    if not res.get("ok"):
        user = res.get("user")
        if user:
            embed = discord.Embed(
                title="⚠️ Đạo hữu đã nhập đạo rồi",
                description=f"{ctx.author.mention}\n🌟 Linh căn: **{user['linh_can']}**\n📜 Cảnh giới: **{res.get('realm_text', 'Phàm Nhân')}**",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return
        await ctx.send("❌ Không thể tạo nhân vật.")
        return

    user = res["user"]
    origin = res["origin"]
    embed = discord.Embed(title="🌌 THIÊN ĐẠO - HÀNH TRÌNH NHẬP ĐẠO", color=discord.Color.blue())
    embed.add_field(name="Tu sĩ", value=ctx.author.mention, inline=False)
    embed.add_field(name="Mô-típ khởi đầu", value=f"**{origin['name']}**", inline=False)
    embed.add_field(name="Lời dẫn chuyện", value=origin["lore"], inline=False)
    embed.add_field(name="🌟 Linh căn", value=f"**{user['linh_can']}**", inline=True)
    embed.add_field(name="💎 Linh thạch", value=f"**{user['linh_thach']}**", inline=True)
    embed.add_field(name="Hướng dẫn tiếp theo", value=f"Dùng **{PREFIX}congphap kiem/phap/the** để chọn công pháp khởi đầu.", inline=False)
    await ctx.send(embed=embed)


@bot.command(name="congphap", aliases=["cong-phap", "path"])
async def congphap(ctx, *, choice: str = None):
    if not choice:
        embed = discord.Embed(
            title="📖 Chọn công pháp",
            description=(
                f"`{PREFIX}congphap kiem` - Kiếm Tu\n"
                f"`{PREFIX}congphap phap` - Pháp Tu\n"
                f"`{PREFIX}congphap the` - Thể Tu"
            ),
            color=discord.Color.blurple()
        )
        await ctx.send(embed=embed)
        return

    res = await api_post("/user/congphap", {"user_id": ctx.author.id, "choice": choice})
    if not res.get("ok"):
        err = res.get("error")
        if err == "already_chosen":
            await ctx.send(f"⚠️ {ctx.author.mention} đã chọn công pháp rồi: **{res['user']['cong_phap_name']}**")
        elif err == "invalid_choice":
            await ctx.send("❌ Công pháp không hợp lệ. Chọn: **kiem / phap / the**")
        else:
            await ctx.send("❌ Không chọn được công pháp.")
        return

    path = res["path"]
    embed = discord.Embed(title="⚔️ Đã chọn công pháp", color=discord.Color.green())
    embed.add_field(name="Tu sĩ", value=ctx.author.mention, inline=False)
    embed.add_field(name="Công pháp", value=f"**{path['name']}**", inline=True)
    embed.add_field(name="Mô tả", value=path["lore"], inline=False)
    embed.add_field(name="Chỉ số khởi đầu", value=f"HP +{path['hp']} | MP +{path['mp']} | ATK +{path['atk']} | DEF +{path['defense']}", inline=False)
    await ctx.send(embed=embed)


@bot.command(name="profile", aliases=["thongtin", "info"])
async def profile(ctx):
    res = await api_get("/user/profile", {"user_id": ctx.author.id})
    if not res.get("ok"):
        await ctx.send(f"❌ {ctx.author.mention} chưa đăng ký! Dùng **{PREFIX}start** để bắt đầu.")
        return

    user = res["user"]
    user["id"] = ctx.author.id
    embed = build_profile_embed({"user": user, "realm_text": res["realm_text"]})
    await ctx.send(embed=embed)


@bot.command(name="lore")
async def lore(ctx):
    res = await api_get("/user/profile", {"user_id": ctx.author.id})
    if not res.get("ok"):
        await ctx.send(f"❌ {ctx.author.mention} chưa đăng ký! Dùng **{PREFIX}start** trước.")
        return
    user = res["user"]
    embed = discord.Embed(title="📖 HÀNH TRÌNH NHẬP ĐẠO", color=discord.Color.purple())
    embed.add_field(name="Mô-típ khởi đầu", value=user["origin_name"], inline=False)
    embed.add_field(name="Lời dẫn", value=user["origin_lore"], inline=False)
    embed.add_field(name="Công pháp", value=user["cong_phap_name"], inline=True)
    await ctx.send(embed=embed)


@bot.command(name="diemdanh")
async def diemdanh(ctx):
    res = await api_post("/user/daily", {"user_id": ctx.author.id})
    if not res.get("ok"):
        if res.get("error") == "cooldown":
            await ctx.send(f"⏳ Bạn đã điểm danh rồi. Thử lại sau **{res['remain']} giây**.")
        else:
            await ctx.send("❌ Không thể điểm danh.")
        return
    await ctx.send(embed=discord.Embed(
        title="📅 Điểm danh thành công",
        description=f"{ctx.author.mention} nhận được **{res['reward']} linh thạch** 💎",
        color=discord.Color.green()
    ))


@bot.command(name="tuluyen", aliases=["tuuyen"])
async def tuluyen(ctx):
    res = await api_post("/user/train", {"user_id": ctx.author.id})
    if not res.get("ok"):
        if res.get("error") == "need_breakthrough":
            await ctx.send(f"⚠️ Bạn đã ở **{res['realm_text']}**.\nHãy dùng **{PREFIX}dotpha** để đột phá đại cảnh giới.")
        elif res.get("error") == "not_enough_linh_thach":
            await ctx.send(f"❌ Không đủ linh thạch để tu luyện.\nCần **{res['need']:,}**.")
        else:
            await ctx.send("❌ Không thể tu luyện.")
        return

    realm_text = res.get("realm_text", "Phàm Nhân")
    await ctx.send(embed=discord.Embed(
        title="🌌 Tu luyện thành công",
        description=f"{ctx.author.mention} đã tiến bộ.
Cảnh giới hiện tại: **{realm_text}**",
        color=discord.Color.purple()
    ))


@bot.command(name="dotpha")
async def dotpha(ctx):
    res = await api_post("/user/breakthrough", {"user_id": ctx.author.id})
    if not res.get("ok"):
        mapping = {
            "not_started": "❌ Bạn chưa bước vào bất kỳ đại cảnh giới nào để đột phá.",
            "not_ready": f"❌ Bạn chưa đạt **Viên Mãn** để đột phá.\nHiện tại: **{res.get('realm_text','')}**",
            "max_realm": "🏁 Bạn đã đạt đại cảnh giới cuối cùng rồi.",
            "not_enough_linh_thach": f"❌ Bạn không đủ linh thạch để đột phá.\nCần **{res['need']:,}**.",
        }
        await ctx.send(mapping.get(res.get("error"), "❌ Không thể đột phá."))
        return

    if res["success"]:
        embed = discord.Embed(title="⚡ Đột phá thành công", description=f"{ctx.author.mention} đã bước sang **{res.get('realm_text', 'cảnh giới mới')}**!", color=discord.Color.orange())
        embed.add_field(name="Tỉ lệ thành công", value=f"**{res['rate']}%**", inline=True)
        embed.add_field(name="Linh thạch đã trừ", value=f"**{res['break_cost']:,}**", inline=True)
    else:
        embed = discord.Embed(title="💥 Đột phá thất bại", color=discord.Color.red())
        embed.add_field(name="Phản phệ", value=f"-{res['backlash_hp']} HP", inline=True)
        embed.add_field(name="Linh thạch mất thêm", value=f"-{res['extra_loss']:,}", inline=True)
        embed.add_field(name="Tình trạng", value="Bị tụt 1 tiểu cảnh giới" if res["dropped"] else "Không tụt cảnh giới", inline=False)
        embed.add_field(name="Tỉ lệ thành công", value=f"**{res['rate']}%**", inline=True)
    await ctx.send(embed=embed)


@bot.command(name="helpgame")
async def helpgame(ctx):
    embed = discord.Embed(title="📖 Hướng dẫn dùng bot Thiên Đạo", color=discord.Color.blurple())
    embed.description = (
        f"`{PREFIX}start` - Nhập đạo\n"
        f"`{PREFIX}congphap kiem/phap/the` - Chọn công pháp\n"
        f"`{PREFIX}profile` - Xem hồ sơ\n"
        f"`{PREFIX}lore` - Xem lại phần mở đầu\n"
        f"`{PREFIX}diemdanh` - Nhận linh thạch\n"
        f"`{PREFIX}tuluyen` - Tu luyện tăng tiểu cảnh giới\n"
        f"`{PREFIX}dotpha` - Đột phá đại cảnh giới\n"
    )
    await ctx.send(embed=embed)


if not TOKEN:
    raise RuntimeError("Missing DISCORD_TOKEN")

bot.run(TOKEN)
