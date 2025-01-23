import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from datetime import datetime
from bson import ObjectId

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

ROUTE_NAME, SECTOR, CRAG, ASCENT_TYPE, SEND_TYPE, GRADE, DATE, LOCATION, NOTES = range(9)

class AscentBuilder:
    def __init__(self):
        self.ascent = {}
        self.ascent._id = ObjectId()
        self.ascent.created_at = int(datetime.now().timestamp())
        self.ascent.updated_at = 0
        self.ascent.deleted_at = 0
        
    def set_route_name(self, route_name):
        self.ascent["route_name"] = route_name

    def set_sector(self, sector):
        self.ascent["sector"] = sector

    def set_crag(self, crag):
        self.ascent["crag"] = crag

    def set_ascent_type(self, ascent_type):
        self.ascent["type"] = ascent_type

    def set_send_type(self, send_type):
        self.ascent["send_type"] = send_type

    def set_grade(self, grade):
        self.ascent["grade"] = grade

    def set_date(self, date):
        self.ascent["date"] = int(datetime.strptime(date, "%d/%m/%Y").timestamp())

    def set_location(self, latitude, longitude):
        self.ascent["location"] = {"latitude": latitude, "longitude": longitude}

    def set_notes(self, notes):
        self.ascent["notes"] = notes
    
    def set_user_id(self, user_id):
        self.ascent["user_id"] = user_id

    def get_ascent(self):
        return self.ascent
    
    def build(self):
        return self.ascent
        
    

class logAscent:
    def __init__(self, mongo_client):
        self.mongo_client = mongo_client
        self.ascent = AscentBuilder()
        
    def get_user(self, telegram_id):
        return self.mongo_client.users.find_one({"telegram_id": telegram_id, "deleted_at": 0})
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Starts the conversation and asks the user about the route name"""
        logger.info("User started the conversation")
        self.ascent.set_user_id(self.get_user(telegram_id=update.message.from_user.id)["_id"])
        await update.message.reply_text(
            "Olá! Vamos começar a registrar a sua escalada. Qual é o nome da via que você escalou?",
            # reply_markup=ReplyKeyboardRemove(),
        )

        return ROUTE_NAME
    
    async def route_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Stores the inputed route name and asks for the sector."""
        self.ascent.set_route_name(update.message.text)
        logger.info(f"Route name of the user: {self.ascent['route_name']}")
        await update.message.reply_text(
            f"Qual é o setor da escalada?\n\nSe você quiser pular essa etapa, digite /pular.",
        )
        return SECTOR
    
    async def sector(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Stores the inputed sector and asks for crag name."""
        self.ascent.set_sector(update.message.text)
        logger.info(f"Sector of the user: {self.ascent['sector']}")
        await update.message.reply_text(
            f"Qual é o nome do pico?\n\nSe você quiser pular essa etapa, digite /pular.",
        )

        return CRAG
    
    async def crag(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Stores the inputed crag and asks for ascent type."""
        self.ascent.set_crag(update.message.text)
        logger.info(f"Crag of the user: {self.ascent['crag']}")
        ascent_types = [["Top Rope", "Guiada", "Boulder", "Free Solo"]]
        await update.message.reply_text(
            f"""Qual foi a modalidade de escalada? Se você quiser pular essa etapa, digite /pular.""",
            reply_markup=ReplyKeyboardMarkup(ascent_types, one_time_keyboard=True),
        )

        return ASCENT_TYPE
    
    async def crag_skip(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Skips the crag iteration"""
        ascent_types = [["Top Rope", "Guiada", "Boulder", "Free Solo"]]
        await update.message.reply_text(
            f"Qual foi a modalidade de escalada?\n\nSe você quiser pular essa etapa, digite /pular.",
            reply_markup=ReplyKeyboardMarkup(ascent_types, one_time_keyboard=True),
        )

        return ASCENT_TYPE
    
    async def ascent_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Stores the inputed ascent type and asks for grade."""
        self.ascent.set_ascent_type(update.message.text)
        logger.info(f"Ascent type of the user: {self.ascent['type']}")
        send_types = [["Redpoint", "Flash", "À Vista", "À Vista Sacando"]]
        await update.message.reply_text(
            f"Você mandou em?\n\nSe você quiser pular essa etapa, digite /pular.",
            reply_markup=ReplyKeyboardMarkup(send_types, one_time_keyboard=True),
        )

        return SEND_TYPE
    
    async def ascent_type_skip(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Skips the ascent type iteration"""
        send_types = [["Redpoint", "Flash", "À Vista", "À Vista Sacando"]]
        await update.message.reply_text(
            f"Você mandou em?\n\nSe você quiser pular essa etapa, digite /pular.",
            reply_markup=ReplyKeyboardMarkup(send_types, one_time_keyboard=True),
        )

        return SEND_TYPE
    
    async def send_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Stores the inputed send type and asks for grade."""
        self.ascent.set_send_type(update.message_text)
        logger.info(f"Send type of the user: {self.ascent['send_type']}")
        await update.message.reply_text(
            f"Qual é a graduação da via? (informar em grau brasileiro)\n\nSe você quiser pular essa etapa, digite /pular.",
        )

        return GRADE
    
    async def send_type_skip(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Skips the send type iteration"""
        await update.message.reply_text(
            f"Qual é a graduação da via? (informar em grau brasileiro)\n\nSe você quiser pular essa etapa, digite /pular.",
        )

        return GRADE
    
    async def grade(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Stores the inputed grade and asks for date."""
        self.ascent.set_grade(update.message_text)
        logger.info(f"Grade of the user: {self.ascent['grade']}")
        await update.message.reply_text(
            f"Qual foi a data da escalada?\n Por favor, informe no formato DD/MM/AAAA.\n\nSe você quiser pular essa etapa, digite /pular.",
        )

        return DATE
    
    async def grade_skip(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Skips the grade iteration"""
        await update.message.reply_text(
            f"Qual foi a data da escalada?\n Por favor, informe no formato DD/MM/AAAA.\n\nSe você quiser pular essa etapa, digite /pular.",
        )

        return DATE
    
    async def date(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Stores the inputed date and asks for location."""
        self.ascent.set_date(update.message.text)
        logger.info(f"Date of the user: {self.ascent['date']}")
        await update.message.reply_text(
            f"Qual é a localização da escalada? Basta compartilhar sua localização comigo!.\n\nSe você quiser pular essa etapa, digite /pular.",
            reply_markup=ReplyKeyboardRemove(),
        )

        return LOCATION
    
    async def date_skip(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Skips the date iteration"""
        await update.message.reply_text(
            f"Qual é a localização da escalada? Basta compartilhar sua localização comigo!.\n\nSe você quiser pular essa etapa, digite /pular.",
            reply_markup=ReplyKeyboardRemove(),
        )

        return LOCATION
    
    async def location(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Stores the inputed location and asks for notes."""
        self.ascent.set_location(update.message.location.latitude, update.message.location.longitude)
        logger.info(f"Location of the user: {self.ascent['location']}")
        await update.message.reply_text(
            f"Você quer adicionar alguma observação sobre a escalada?\n\nSe você quiser pular essa etapa, digite /pular.",
        )

        return NOTES
    
    async def location_skip(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Skips the location iteration"""
        await update.message.reply_text(
            f"Você quer adicionar alguma observação sobre a escalada?\n\nSe você quiser pular essa etapa, digite /pular.",
        )

        return NOTES
    
    async def notes(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Stores the inputed notes and finishes the conversation."""
        self.ascent.set_notes(update.message.text)
        logger.info(f"Notes of the user: {self.ascent['notes']}")
        self.mongo_client.ascents.insert_one(self.ascent)
        await update.message.reply_text(
            "Obrigado por registrar a sua escalada! Se precisar de mais alguma coisa, estou por aqui.",
        )

        return ConversationHandler.END
    
    async def notes_skip(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Skips the current iteration"""
        await update.message.reply_text(
            "Ok, vamos pular essa etapa."
        )

        return ConversationHandler.END
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancels and ends the conversation."""
        await update.message.reply_text(
            "Ok, cancelando o registro da sua cadena."
        )

        return ConversationHandler.END
    
    
    def get_handler(self):
        return ConversationHandler(
            entry_points=[CommandHandler("log", self.start)],
            states={
                ROUTE_NAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.route_name),
                ],
                SECTOR: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.sector),
                ],
                CRAG: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.crag),
                    CommandHandler("pular", self.crag_skip),
                ],
                ASCENT_TYPE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.ascent_type),
                    CommandHandler("pular", self.ascent_type_skip),
                ],
                SEND_TYPE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.send_type),
                    CommandHandler("pular", self.send_type_skip),
                ],
                GRADE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.grade),
                    CommandHandler("pular", self.grade_skip),
                ],
                DATE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.date),
                    CommandHandler("pular", self.date_skip),
                ],
                LOCATION: [
                    MessageHandler(filters.LOCATION & ~filters.COMMAND, self.location),
                    CommandHandler("pular", self.location_skip),
                ],
                NOTES: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.notes),
                    CommandHandler("pular", self.notes_skip),
                ],
            },
            fallbacks=[CommandHandler("cancelar", self.cancel)],
        )