import json
import os
import asyncio
from rubka import Robot

# ⚠️ توکن خودت رو اینجا بذار
TOKEN = "CFCIGC0WIWJFSIRMILWIZEWKAQAYRILWRCDPGRXCPRKGAKDVSNNDSGEEAUVRNYHQ"
bot = Robot(TOKEN)

FIXED_MEMBERS = ["سیرانی", "صفرزاده", "عرشیا", "خرم", "سید", "رسول", "نوآذر", "مجتبی", "نصیری", "فراهانی"]
CAPACITY = 12
PRICE_FIXED = 70
PRICE_GUEST = 100
CARD_NUMBER = "6037997269607413"

DATA_FILE = "football_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"present": {}, "paid": {}, "debts": {}, "credits": {}, "monthly_sessions": 4}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def show_list(data):
    present = data["present"]
    paid = data["paid"]
    debts = data["debts"]
    credits = data.get("credits", {})
    
    if not present:
        lines = ["📋 لیست خالیه. برای ثبت بنویس: `میام [اسم]`"]
    else:
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
    
    active_debts = {k: v for k, v in debts.items() if v > 0}
    if active_debts:
        lines.append("\n🔴 بدهکاران هفته‌های گذشته:")
        for name, amount in active_debts.items():
            lines.append(f"🔴 {name} — {amount} تومان")
    
    lines.append(f"\n💳 شماره کارت جهت واریز:\n`{CARD_NUMBER}`")
    return "\n".join(lines)

def clean_name(name):
    words = name.split()
    ignore_words = ["شد", "کردم", "کرد", "را", "و", "هست", "نیست"]
    cleaned = [w for w in words if w not in ignore_words]
    return " ".join(cleaned)

def parse_command(text):
    text = text.strip()
    
    long_actions = {
        "تنظیم جلسات": "set_sessions",
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

@bot.on_message()
async def handle(bot, message):
    text = (message.text or "").strip()
    data = load_data()
    
    if text in ["/start", "/help"]:
        await message.reply(
            "سلام! ⚽ بات مدیریت فوتبال گیاه‌شناسی\n\n"
            "دستورها:\n"
            "`تنظیم جلسات [عدد]` — تعیین تعداد جلسات ماه (پیش‌فرض ۴)\n"
            "`پرداخت ماهانه [اسم]` — اضافه شدن اعتبار\n"
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
        name = clean_name(text[8:].strip())
        debt = data["debts"].get(name, 0)
        paid = data["paid"].get(name, False)
        credit = data.get("credits", {}).get(name, 0)
        
        if name in FIXED_MEMBERS: kind = "ثابت"
        elif name in data["present"]: kind = data["present"][name]
        else: kind = "نامشخص"
        
        msg = f"👤 {name} ({kind})\n"
        if kind == "ثابت":
            if credit > 0: msg += f"💳 اعتبار: {credit} جلسه\n"
            else: msg += "🟢 اعتبار ماهانه تمام شده.\n"
        if debt > 0: msg += f"🔴 بدهی کل: {debt} تومان"
        else: msg += "🟢 بدهی نداری."
        await message.reply(msg)
        return

    if text == "هفته جدید":
        # پاکسازی کامل دیتای حضور برای هفته جدید
        data["present"] = {}
        data["paid"] = {}
        save_data(data)
        await message.reply("🔄 لیست این هفته کاملاً پاک شد. بدهی‌ها و اعتبارها حفظ شدند. آماده هفته جدید!")
        return
        
    if text == "ریست کامل":
        save_data({"present": {}, "paid": {}, "debts": {}, "credits": {}, "monthly_sessions": 4})
        await message.reply("⚠️ کل دیتابیس پاک شد.")
        return
    
    action, name = parse_command(text)
    if not action: return
    
    if action == "set_sessions":
        try:
            count = int(name)
            data["monthly_sessions"] = count
            save_data(data)
            await message.reply(f"✅ تعداد جلسات این ماه روی {count} تنظیم شد.")
        except:
            await message.reply("⚠️ لطفاً یه عدد معتبر وارد کن. (مثال: تنظیم جلسات 5)")
        return

    if action == "monthly_paid":
        if name in FIXED_MEMBERS:
            if "credits" not in data: data["credits"] = {}
            
            current_sessions = data.get("monthly_sessions", 4)
            current_credits = data["credits"].get(name, 0)
            
            used_sessions = max(0, current_sessions - current_credits)
            new_credits_to_add = current_sessions - used_sessions
            
            data["credits"][name] = current_credits + new_credits_to_add
            
            if name in data["debts"]:
                del data["debts"][name]
                
            save_data(data)
            await message.reply(f"✅ پرداخت ماهانه {name} ثبت شد.\n💳 {new_credits_to_add} جلسه اعتبار جدید اضافه شد. (کل اعتبار: {data['credits'][name]} جلسه)")
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
        if kind == "ثابت":
            if data.get("credits", {}).get(name, 0) > 0:
                data["credits"][name] -= 1
                msg_add = f"\n💳 ۱ جلسه کسر شد. (باقی‌مانده: {data['credits'][name]})"
            else:
                price = PRICE_FIXED
                data["debts"][name] = data["debts"].get(name, 0) + price
                msg_add = f"\n🔴 بدهی ۷۰ تومانی این هفته ثبت شد."
                
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
        elif name in FIXED_MEMBERS and name in data["debts"]:
            del data["debts"][name]
            save_data(data)
            await message.reply(f"✅ بدهی {name} تسویه شد.\n\n" + show_list(data))
        else:
            await message.reply(f"⚠️ {name} توی لیست نیست یا بدهی نداره.")

asyncio.run(bot.run())
