import os, json, random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from words import WORDS

TOKEN = os.getenv("BOT_TOKEN")

users = {}

def save():
    with open("users.json", "w") as f:
        json.dump(users, f)

def load():
    global users
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
    except:
        users = {}

def get_user(uid):
    uid = str(uid)
    if uid not in users:
        users[uid] = {"score": 0, "level": "A1"}
    return users[uid]

# 🎯 تعیین سطح ساده
def test_level():
    return random.choice(["A1", "A2"])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    level = test_level()
    user["level"] = level
    save()

    await update.message.reply_text(
        f"🤖 خوش اومدی!\n\n🎯 سطح تو: {level}\n"
        f"💰 dozd: {user['score']}\n\n"
        "برای تمرین /quiz بزن"
    )


async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    level = user["level"]

    word = random.choice(WORDS[level])
    context.user_data["answer"] = word["fa"]

    await update.message.reply_text(f"❓ {word['en']} یعنی چی؟")


async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    text = update.message.text

    correct = context.user_data.get("answer")

    if not correct:
        await update.message.reply_text("اول /quiz بزن 😄")
        return

    if text == correct:
        user["score"] += 10
        msg = "✅ درست! +10 dozd"
    else:
        user["score"] -= 1
        msg = f"❌ غلط! جواب: {correct} (-1 dozd)"

    save()
    context.user_data["answer"] = None

    await update.message.reply_text(f"{msg}\n💰 امتیاز: {user['score']}")


async def addword(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # فقط برای تو (ادمین ساده)
    try:
        level, en, fa = context.args
        WORDS[level].append({"en": en, "fa": fa})
        await update.message.reply_text("✅ اضافه شد")
    except:
        await update.message.reply_text("فرمت: /addword A1 apple سیب")


def main():
    load()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CommandHandler("addword", addword))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))

    app.run_polling()


if __name__ == "__main__":
    main()
