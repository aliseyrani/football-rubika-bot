
import os
import asyncio
from rubka.asynco import Robot, Message

TOKEN = os.getenv("BOT_TOKEN")

bot = Robot(TOKEN)

@bot.on_message()
async def handle_message(message: Message):
    text = (message.text or "").strip()

    if text == "/start":
        await message.reply(
            "سلام! ⚽\n"
            "به ربات مدیریت فوتبال خوش اومدی.\n\n"
            "برای دیدن امکانات بنویس: /football"
        )

    elif text == "/football":
        await message.reply(
            "⚽ مدیریت فوتبال هفتگی\n\n"
            "🗓 یکشنبه‌ها، ساعت ۱۹:۳۰ تا ۲۱\n"
            "💰 هزینه هر جلسه: ۶۲۰ هزار تومان\n\n"
            "برای شروع، حضور خودت رو اعلام کن:\n"
            "برای حضور بنویس: میام\n"
            "برای عدم حضور بنویس: نمیام\n\n"
            "این نسخه آزمایشی اولیه است؛ "
            "هنوز حضور و پرداخت را ذخیره نمی‌کند."
        )

    elif text == "میام":
        await message.reply("✅ اعلام حضورت دریافت شد؛ ثبت نهایی هنوز فعال نیست.")

    elif text == "نمیام":
        await message.reply("❌ پیام عدم حضورت دریافت شد؛ ثبت نهایی هنوز فعال نیست.")

async def main():
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
