import json
import telegram
import os
import asyncio
from logging import getLogger
logger = getLogger(__name__)

from commands import Command

bot = telegram.Bot(os.environ["TELEGRAM_BOT_TOKEN"])
    
async def send_default_message(chat_id):
    await bot.sendMessage(chat_id=chat_id, text="Eu sou um bot que registra cadenas de escalada.\n\nEnvie /help para ver os comandos disponíveis e comece a registrar suas cadenas!")

def handler(event, context):
    body = json.loads(event["body"])
    print("Received body: ", body)
    chat_id = body["message"]["chat"]["id"]
    text = body["message"]["text"]
    if "/" in text[0]:
        command = Command(text, bot, chat_id)
        try:
            command_response = asyncio.run(command.run(text))
            logger.info(f"Command response: {command_response}")
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "chat_id": chat_id,
                    "text": command_response
                })
            }
        except Exception as e:
            logger.error(f"Error trying to execute a command: {e}")
            return {
                "statusCode": 200
            }
    else:
        asyncio.run(send_default_message(chat_id))
    return {
        "statusCode": 200
    }
    
