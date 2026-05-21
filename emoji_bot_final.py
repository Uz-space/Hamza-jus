"""
Telegram Animatsion Emoji Bot
==============================
O'rnatish:
    pip install aiogram fonttools

Ishlatish:
    python emoji_bot.py

Xususiyatlar:
- 2 ta tayyor animatsion dizayn (fon)
- Poppins Bold shrifti bilan har qanday so'z
- Telegram Stars to'lov tizimi (ixtiyoriy)
- /start, /help buyruqlari
"""

import gzip
import json
import base64
import os
import logging
import tempfile
from io import BytesIO

from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ============================================================
#  SOZLAMALAR
# ============================================================
BOT_TOKEN = "BU_YERGA_BOT_TOKENINGIZNI_YOZING"
FONT_PATH = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
FONT_SIZE = 105       # Harflar kattaligi (512x512 canvas uchun)
MAX_CHARS = 10        # Maksimal harf soni
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ---- Shablonlar (TGS base64 formatida ichiga joylashtirilgan) ----
TEMPLATE_1_B64 = """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"""

TEMPLATE_2_B64 = """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"""

TEMPLATES = {
    "1": ("🌟 Dizayn 1 (asosiy)", TEMPLATE_1_B64),
    "2": ("✨ Dizayn 2 (sodda)",  TEMPLATE_2_B64),
}

# ---- Shrift yuklash ----
_font = TTFont(FONT_PATH)
_glyf_set = _font.getGlyphSet()
_cmap = _font.getBestCmap()
_upm = _font["head"].unitsPerEm  # 1000


def _char_paths(char, scale, ox, oy):
    """Bir harf uchun Lottie contour larini qaytaradi."""
    gname = _cmap.get(ord(char.upper()))
    if not gname:
        return [], 0

    adv = _glyf_set[gname].width * scale
    pen = RecordingPen()
    _glyf_set[gname].draw(pen)

    contours, cur_v, cur_i, cur_o = [], [], [], []

    def tx(x): return round(x * scale + ox, 2)
    def ty(y): return round(-y * scale + oy, 2)

    for op, args in pen.value:
        if op == "moveTo":
            if cur_v:
                contours.append({"c": True, "v": cur_v, "i": cur_i, "o": cur_o})
            x, y = args[0]
            cur_v, cur_i, cur_o = [[tx(x), ty(y)]], [[0, 0]], [[0, 0]]

        elif op == "lineTo":
            cur_o[-1] = [0, 0]
            x, y = args[0]
            cur_v.append([tx(x), ty(y)])
            cur_i.append([0, 0])
            cur_o.append([0, 0])

        elif op == "curveTo":
            pts = list(args)
            c1, c2, end = pts[0], pts[-2], pts[-1]
            prev = cur_v[-1]
            cur_o[-1] = [round(tx(c1[0]) - prev[0], 2),
                         round(ty(c1[1]) - prev[1], 2)]
            ex, ey = tx(end[0]), ty(end[1])
            cur_v.append([ex, ey])
            cur_i.append([round(tx(c2[0]) - ex, 2),
                          round(ty(c2[1]) - ey, 2)])
            cur_o.append([0, 0])

        elif op in ("closePath", "endPath"):
            if cur_v:
                contours.append({"c": True, "v": cur_v, "i": cur_i, "o": cur_o})
                cur_v, cur_i, cur_o = [], [], []

    if cur_v:
        contours.append({"c": True, "v": cur_v, "i": cur_i, "o": cur_o})

    return contours, adv


def _build_text_layer(text, canvas_w=512, canvas_h=512, font_size=FONT_SIZE):
    """Matn uchun yangi Lottie shape layer yasaydi."""
    scale = font_size / _upm
    text = text.upper()

    # Umumiy kenglik (markazlash uchun)
    total_w = 0
    char_info = []
    for ch in text:
        gname = _cmap.get(ord(ch))
        adv = (_glyf_set[gname].width if gname else int(_upm * 0.5)) * scale
        char_info.append((ch, adv))
        total_w += adv

    cur_x = (canvas_w - total_w) / 2 - canvas_w / 2
    baseline_y = font_size * 0.28

    shapes = []
    for ch, adv in char_info:
        if ch == " ":
            cur_x += adv
            continue
        for contour in _char_paths(ch, scale, cur_x, baseline_y)[0]:
            shapes.append({"ty": "sh", "nm": f"L_{ch}",
                           "ks": {"a": 0, "k": contour}})
        cur_x += adv

    shapes += [
        {"ty": "fl", "nm": "Fill",
         "o": {"a": 0, "k": 100},
         "c": {"a": 0, "k": [1, 1, 1, 1]}, "r": 1},
        {"ty": "tr",
         "a": {"a": 0, "k": [0, 0]},
         "p": {"a": 0, "k": [canvas_w / 2, canvas_h / 2]},
         "s": {"a": 0, "k": [100, 100]},
         "r": {"a": 0, "k": 0},
         "o": {"a": 0, "k": 100},
         "sk": {"a": 0, "k": 0},
         "sa": {"a": 0, "k": 0}},
    ]

    return {
        "ty": 4, "nm": "CustomText", "mn": "custom_text",
        "ddd": 0, "ind": 99, "sr": 1, "ip": 0, "op": 180,
        "st": 0, "bm": 0, "ao": 0,
        "ks": {
            "a": {"a": 0, "k": [0, 0]},
            "p": {"a": 0, "k": [0, 0]},
            "s": {"a": 0, "k": [100, 100]},
            "r": {"a": 0, "k": 0},
            "o": {"a": 0, "k": 100},
            "sk": {"a": 0, "k": 0},
            "sa": {"a": 0, "k": 0},
        },
        "shapes": [{"ty": "gr", "nm": "TG", "it": shapes}],
    }


def generate_tgs(user_text, template_b64, font_size=FONT_SIZE):
    """Shablon + yangi matn => TGS baytlari."""
    raw = gzip.decompress(base64.b64decode(template_b64))
    data = json.loads(raw)

    # Eski TextGroup layerini olib tashlash
    data["layers"] = [
        layer for layer in data["layers"]
        if not any(
            item.get("nm") == "TextGroup"
            for shape in layer.get("shapes", [])
            for item in shape.get("it", [])
        )
    ]

    # Yangi matn layerini qo'shish
    data["layers"].append(
        _build_text_layer(user_text, data.get("w", 512),
                          data.get("h", 512), font_size)
    )

    out = BytesIO()
    with gzip.GzipFile(fileobj=out, mode="wb") as gz:
        gz.write(json.dumps(data, ensure_ascii=False,
                            separators=(",", ":")).encode())
    return out.getvalue()


# ---- Foydalanuvchi holati (xotira) ----
user_state = {}   # {user_id: {"text": str}}

# ---- Bot ----
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


def design_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    for key, (label, _) in TEMPLATES.items():
        kb.insert(InlineKeyboardButton(label, callback_data=f"design:{key}"))
    return kb


@dp.message_handler(commands=["start", "help"])
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Salom! Men animatsion emoji yasayman.\n\n"
        f"📝 Menga {MAX_CHARS} harfgacha so'z yuboring\n"
        "   (masalan: ALIBEK, TOP, ALPHA, VIP)\n\n"
        "⚡ Keyin dizayn tanlang — emoji 5 soniyada tayyor!\n"
        "⚠️  Emojidan foydalanish uchun Telegram Premium kerak."
    )


@dp.message_handler(lambda m: m.text and not m.text.startswith("/"))
async def handle_text(message: types.Message):
    text = message.text.strip()

    if len(text) > MAX_CHARS:
        await message.answer(
            f"⚠️ So'z {MAX_CHARS} ta harfdan oshmasin! "
            f"Siz {len(text)} ta harf yubordingiz."
        )
        return
    if not text.replace(" ", "").isalpha():
        await message.answer("⚠️ Faqat lotin harflari yuboring (A-Z).")
        return

    user_state[message.from_user.id] = {"text": text}
    await message.answer(
        f"✅ So'z qabul qilindi: <b>{text.upper()}</b>\n\n"
        "Quyidagi dizaynlardan birini tanlang:",
        parse_mode="HTML",
        reply_markup=design_keyboard()
    )


@dp.callback_query_handler(lambda c: c.data.startswith("design:"))
async def handle_design(callback: types.CallbackQuery):
    uid = callback.from_user.id
    design_key = callback.data.split(":")[1]

    state = user_state.get(uid)
    if not state:
        await callback.answer("❌ Avval so'z yuboring!", show_alert=True)
        return

    user_text = state["text"].upper()
    _, template_b64 = TEMPLATES[design_key]

    await callback.answer("⏳ Yaratilmoqda...")
    status = await callback.message.answer("⏳ Emojingiz yasalmoqda...")

    try:
        tgs_bytes = generate_tgs(user_text, template_b64)

        buf = BytesIO(tgs_bytes)
        buf.name = f"{user_text}.tgs"

        await callback.message.answer_document(
            buf,
            caption=(
                f"✨ <b>{user_text}</b> emojingiz tayyor!\n\n"
                "📌 Telegram > Sticker yoki Emoji paketingizga qo'shing."
            ),
            parse_mode="HTML"
        )
        await status.delete()

    except Exception as e:
        logging.error(f"Xatolik: {e}", exc_info=True)
        await status.edit_text(f"❌ Xatolik yuz berdi: {e}")


if __name__ == "__main__":
    logging.info("Bot ishga tushdi...")
    executor.start_polling(dp, skip_updates=True)
