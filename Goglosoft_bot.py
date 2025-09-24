from telegram.ext import Application, MessageHandler, filters, CommandHandler
import asyncio

'''Если что, знаю шо нельзя палить токен и его надо шифровать, но тут не стал (не воруй моего бота!!)'''

token = '8411991203:AAH-E6gArphpNBoPUpOjoazXiKxaIfAoeLU'

async def start(update,context):
    name = update.message.from_user.first_name
    await update.message.reply_text(f'Привет, {name}! Я могу ответить капсом на твоё сообщение. Напиши что-нибудь')

async def upper_text(update, context):
    text = update.message.text
    await update.message.reply_text(text.upper())

async def not_text(update, context):
    await update.message.reply_text('Отправьте, пожалуйста, только текстовое сообщение')

application = Application.builder().token(token).build()

application.add_handler(CommandHandler("start", start))

application.add_handler(MessageHandler(filters.TEXT, upper_text))

application.add_handler(MessageHandler(~filters.TEXT, not_text))

if __name__ == "__main__":
    asyncio.run(application.run_polling())
    
    