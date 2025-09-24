from telegram.ext import Application, MessageHandler, filters, CommandHandler
import asyncio
import aiosqlite
from db import init_db

'''Если что, знаю шо нельзя палить токен и его надо шифровать, но тут не стал (не воруй моего бота!!)'''

token = '8411991203:AAH-E6gArphpNBoPUpOjoazXiKxaIfAoeLU'

async def log(user_id, action):
    async with aiosqlite.connect("bot.db") as db:
        await db.execute(
            "INSERT INTO logs (user_id, action) VALUES (?, ?)",
            (user_id, action)
        )
        await db.commit()


async def start(update,context):
    telegram_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    last_name = update.message.from_user.last_name

    async with aiosqlite.connect("bot.db") as db:
        cursor = await db.execute(
            "SELECT id FROM users WHERE telegram_id = ?", (telegram_id,)
        )
        row = await cursor.fetchone()

        if row is None:
            cursor = await db.execute(
                "INSERT INTO users (telegram_id, first_name, last_name) VALUES (?, ?, ?)",
                (telegram_id, first_name, last_name)
            )
            await db.commit()

            new_user_id = cursor.lastrowid
            await log(new_user_id, "registration")

        else:
            new_user_id = row[0]
            await log(new_user_id, "start")

    await update.message.reply_text(f"Привет, {first_name}! Я могу ответить капсом на твоё сообщение. Напиши что-нибудь")


async def upper_text(update, context):
    telegram_id = update.message.from_user.id
    text = update.message.text

    async with aiosqlite.connect("bot.db") as db:
        cursor = await db.execute(
            "SELECT id FROM users WHERE telegram_id = ?", (telegram_id,)
        )
        row = await cursor.fetchone()
        if row is None:
            await update.message.reply_text(
                'Вы ещё не зарегистрированы! Введите /start для регистрации'
            )
            return

        user_id = row[0]

        await log(user_id, "message")

    await update.message.reply_text(text.upper())


async def not_text(update, context):
    telegram_id = update.message.from_user.id

    async with aiosqlite.connect("bot.db") as db:
        cursor = await db.execute(
            "SELECT id FROM users WHERE telegram_id = ?", (telegram_id,)
        )
        row = await cursor.fetchone()
        if row is None:
            await update.message.reply_text(
                'Вы ещё не зарегистрированы! Введите /start для регистрации'
            )
            return

        user_id = row[0]

        await log(user_id, "not_text")

    await update.message.reply_text('Отправьте, пожалуйста, только текстовое сообщение')

async def history(update, context):
    telegram_id = update.message.from_user.id

    async with aiosqlite.connect("bot.db") as db:
        cursor = await db.execute(
            "SELECT id FROM users WHERE telegram_id = ?", (telegram_id,)
        )
        row = await cursor.fetchone()
        if row is None:
            await update.message.reply_text('Вы ещё не зарегистрированы! Введите "/start" для регистрации')
            return

        user_id = row[0]

        cursor = await db.execute(
            "SELECT action, dt FROM logs WHERE user_id = ? ORDER BY dt DESC LIMIT 10", (user_id,)
        )
        rows = await cursor.fetchall()

        hist = []
        for action, dt in rows:
            hist.append(f"{dt}: {action}")

        await  update.message.reply_text("Вот история твоих последних 10 действий:\n" + "\n".join(hist))

application = Application.builder().token(token).build()

application.add_handler(CommandHandler("start", start))

application.add_handler(CommandHandler("history", history))

application.add_handler(MessageHandler(filters.TEXT, upper_text))

application.add_handler(MessageHandler(~filters.TEXT, not_text))


async def main():
    await init_db()
    await application.run_polling()

if __name__ == "__main__":
    application.run_polling()
    
    