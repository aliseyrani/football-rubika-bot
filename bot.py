import json
import os
import asyncio
from rubka import Robot

# ⚠️ توکن جدید خودت رو اینجا بذار
TOKEN = "CFCIGC0WIWJFSIRMILWIZEWKAQAYRILWRCDPGRXCPRKGAKDVSNNDSGEEAUVRNYHQ"
bot = Robot(TOKEN)

FIXED_MEMBERS = ["سیرانی", "صفرزاده", "عرشیا", "خرم", "سید", "رسول", "نوآذر", "مجتبی", "نصیری", "فراهانی"]
CAPACITY = 12
PRICE_FIXED = 70
PRICE_GUEST = 100
MONTHLY_SESSIONS = 4
CARD_NUMBER = "6037997269607413"

DATA_FILE = "football_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"present": {}, "paid": {}, "debts": {}, "credits": {}, "month_debts": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def show_list(data):
    present = data["present"]
    paid = data["paid"]
    debts = data["debts"]
    credits = data.get("credits", {})
    month_debts = data.get("month_debts", [])
    
    if not present:
        return "📋 لیست خالیه. برای ثبت بنویس: `میام [اسم]`"
    
    lines = [f"⚽ لیست حاضرین ({len(present)}/{CAPACITY}):\n"]
    total = 0
    
    for i, (name, kind) in enumerate(present.items(), 1):
        if kind == "ثابت":
            price = PRICE_FIXED
            if credits.get(name, 0) > 0:
                pay_status = f"✅ (اعتبار: {credits[name]})"
            else:
                pay_status = "✅" if paid.get(name) else "⏳"
                total += price
        elif kind == "مهمان":
            price = PRICE_GUEST
            pay_status = "✅" if paid.get(name) else "⏳"
            total += price
        else: 
            price = 0
            pay_status = "🆓"
            total += price
            
        debt = debts.get(name, 0)
        debt_str = f" | 🔴 بدهی: {debt}" if debt > 0 else ""
        kind_str = f"({kind})" if kind != "رایگان" else "(رایگان 🆓)"
        lines.append(f"{i}. {name} {kind_str} — {price} {pay_status}{debt_str}")
    
    lines.append(f"\n💰 جمع قابل دریافت این هفته: {total} تومان")
    
    if month_debts:
        lines.append(f"\n⚠️ منتظر پرداخت اول ماه: {', '.join(month_debts)}")
    if debts:
        lines.append("\n🔴 بدهکاران هفته قبل:")
        for name, amount in debts.items():
            if amount > 0:
                lines.append(f"🔴 {name} — {amount}")
    
    # اضافه شدن شماره کارت به انتهای لیست
    lines.append(f"\n💳 شماره کارت جهت واریز:\n`{CARD_NUMBER}`")
    
    return "\n".join(lines)

def parse_command(text):
    text = text.strip()
    
    long_actions = {
        "بدهی اول ماه": "month_debts",
        "پرداخت ماهانه": "monthly_paid",
    }
    
    for phrase, act in long_actions.items():
        if text.startswith(phrase + " "):
            name = text[len(phrase):].strip()
            return act, clean_name(name)
        elif text.endswith(" " + phrase):
            name = text[:-len(phrase)].strip()
            return act, clean_name(name)

    words = text.split()
    if len(words) < 2: return None, None
    
    short_actions = {
        "میام": "present", "حاضر": "present",
        "نیام": "absent", "نمیام": "absent",
        "پرداخت": "paid", "رایگان": "free"
    }
    
    action = None
    name_parts = []
    
    for w in words:
        if w in short_actions and action is None:
            action = short_actions[w]
        else:
            name_parts.append(w)
    
    if action and name_parts:
        return action, clean_name(" ".join(name_parts))
    return None, None

# تابع جدید برای پاک کردن کلمات اضافی مثل "شد" و "کردم" از اسم
def clean_name(name):
    words = name.split()
    ignore_words = ["شد", "کردم", "کرد", "را", "و", "هست", "نیست"]
    cleaned = [w for w in words if w not in ignore_words]
    return " ".join(cleaned)

@bot.on_message()
async def handle(bot, message):
    text = (message.text or "").strip()
    data = load_data()
    
    if text in ["/start", "/help"]:
        await message.reply(
            "سلام! ⚽ بات مدیریت فوتبال گیاه‌شناسی\n\n"
            "دستورها:\n"
            "`بدهی اول ماه [اسم‌ها]` — ثبت لیست بدهکاران ماه\n"
            "`پرداخت ماهانه [اسم]` — اضافه شدن ۴ جلسه اعتبار\n"
            "`میام [اسم]` — اعلام حضور\n"
            "`نیام [اسم]` — انصراف\n"
            "`رایگان [اسم]` — ثبت مهمان رایگان\n"
            "`پرداخت [اسم]` — تسویه هفتگی\n"
            "`لیست` — دیدن لیست\n"
            "`حساب من [اسم]` — چک کردن وضعیت\n"
            "`هفته جدید` — پاک کردن لیست برای هفته بعد\n"
            "`ریست کامل` — پاک کردن کل اطلاعات"
        )
        return
    
    if text == "لیست":
        await message.reply(show_list(data))
        return
        
    if text.startswith("حساب من "):
        name = text[8:].strip()
        name = clean_name(name)
        debt = data["debts"].get(name, 0)
        paid = data["paid"].get(name, False)
        credit = data.get("credits", {}).get(name, 0)
        in_month_debts = name in data.get("month_debts", [])
        
        if name in FIXED_MEMBERS: kind = "ثابت"
        elif name in data["present"]: kind = data["present"][name]
        else: kind = "نامشخص"
        
        msg = f"👤 {name} ({kind})\n"
        if kind == "ثابت":
            if in_month_debts: msg += "⚠️ پرداخت اول ماه انجام نشده.\n"
            if credit > 0: msg += f"💳 اعتبار: {credit} جلسه\n"
            elif not in_month_debts: msg += "🟢 اعتبار ماهانه تمام شده.\n"
        if debt > 0: msg += f"🔴 بدهی قبلی: {debt} تومان"
        else: msg += "🟢 بدهی نداری."
        await message.reply(msg)
        return

    if text == "هفته جدید":
        credits = data.get("credits", {})
        for name, kind in data["present"].items():
            if kind == "ثابت" and credits.get(name, 0) > 0:
                continue
            if not data["paid"].get(name, False) and kind != "رایگان":
                price = PRICE_FIXED if kind == "ثابت" else PRICE_GUEST
                data["debts"][name] = data["debts"].get(name, 0) + price
        
        data["present"] = {}
        data["paid"] = {}
        save_data(data)
        await message.reply("🔄 لیست این هفته پاک شد و بدهی‌ها منتقل شد. آماده هفته جدید!")
        return
        
    if text == "ریست کامل":
        save_data({"present": {}, "paid": {}, "debts": {}, "credits": {}, "month_debts": []})
        await message.reply("⚠️ کل دیتابیس پاک شد.")
        return
    
    action, name = parse_command(text)
    if not action: return
    
    if action == "month_debts":
        names = [n.strip() for n in name.replace("،", ",").split(",")]
        data["month_debts"] = names
        save_data(data)
        await message.reply(f"📝 لیست بدهکاران اول ماه ثبت شد:\n" + "\n".join(f"- {n}" for n in names))
        return

    if action == "monthly_paid":
        if name in FIXED_MEMBERS:
            if "credits" not in data: data["credits"] = {}
            data["credits"][name] = data["credits"].get(name, 0) + MONTHLY_SESSIONS
            if name in data.get("month_debts", []):
                data["month_debts"].remove(name)
            save_data(data)
            await message.reply(f"✅ پرداخت ماهانه {name} ثبت شد.\n💳 {MONTHLY_SESSIONS} جلسه اعتبار اضافه شد.")
        else:
            await message.reply(f"⚠️ {name} جزو نفرات ثابت نیست.")
        return

    if action == "present":
        if name in data["present"]:
            await message.reply(f"⚠️ {name} قبلاً ثبت شده.")
            return
        if len(data["present"]) >= CAPACITY:
            await message.reply(f"❌ ظرفیت تکمیل است ({CAPACITY} نفر).")
            return
        
        kind = "ثابت" if name in FIXED_MEMBERS else "مهمان"
        data["present"][name] = kind
        
        msg_add = ""
        if kind == "ثابت" and data.get("credits", {}).get(name, 0) > 0:
            data["credits"][name] -= 1
            msg_add = f"\n💳 ۱ جلسه کسر شد. (باقی‌مانده: {data['credits'][name]})"
        
        save_data(data)
        price = PRICE_FIXED if kind == "ثابت" else PRICE_GUEST
        await message.reply(f"✅ {name} ({kind}) ثبت شد.{msg_add}\n\n" + show_list(data))
        
    elif action == "free":
        if name in data["present"]:
            await message.reply(f"⚠️ {name} قبلاً ثبت شده.")
            return
        if len(data["present"]) >= CAPACITY:
            await message.reply(f"❌ ظرفیت تکمیل است.")
            return
        data["present"][name] = "رایگان"
        data["paid"][name] = True
        save_data(data)
        await message.reply(f"🆓 {name} (رایگان) ثبت شد.\n\n" + show_list(data))
    
    elif action == "absent":
        if name in data["present"]:
            del data["present"][name]
            data["paid"].pop(name, None)
            save_data(data)
            await message.reply(f"❌ {name} حذف شد.\n\n" + show_list(data))
    
    elif action == "paid":
        if name in data["present"]:
            data["paid"][name] = True
            if name in data["debts"]:
                del data["debts"][name]
            save_data(data)
            await message.reply(f"✅ پرداخت {name} ثبت شد.\n\n" + show_list(data))
        else:
            await message.reply(f"⚠️ {name} توی لیست نیست.")

asyncio.run(bot.run())