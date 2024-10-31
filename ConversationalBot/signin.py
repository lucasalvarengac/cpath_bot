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


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

EMAIL, NAME, GENDER, PHOTO, LOCATION, BIO = range(6)

class SignIn:
    def __init__(self, mongo_client):
        self.mongo_client = mongo_client
        self.user = {
            "name": None,
            "gender": None,
            "photo": None,
            "location": None,
            "bio": None,
            "created_at": None,
            "deleted_at": 0,
        }
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Starts the conversation and asks the user about their name"""
        logger.info("User started the conversation")
        self.user["created_at"] = int(datetime.now().timestamp())
        await update.message.reply_text(
            "Olá! Meu nome é CPath, estou aqui para te ajudar a viver o sonho!\nVamos conversar? Qual é o seu email?\n\nVocê pode cancelar qualquer iteração nossa utilizando o comando /cancelar. ",
            # reply_markup=ReplyKeyboardRemove(),
        )

        return EMAIL
    
    async def email(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Stores the inputed email and asks for a name."""
        self.user["email"] = update.message.text
        mongo_client = self.mongo_client.users.find_one({"email": self.user["email"]})
        if mongo_client:
            await update.message.reply_text(
                "Esse email já está cadastrado. \n\nPor favor, insira um email diferente."
            )
            return ConversationHandler.END
        
        logger.info(f"Email of the user: {self.user['email']}")
        await update.message.reply_text(
            f"Legal! Agora me diga o seu nome.\n\nSe você quiser pular essa etapa, digite /pular.",
            reply_markup=ReplyKeyboardRemove(),
        )

        return NAME
    
    async def name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Stores the inputed name and asks for a gender."""
        self.user["name"] = update.message.text
        logger.info(f"Name of the user: {self.user['name']}")
        reply_keyboard = [["Homem", "Mulher", "Outro"]]
        await update.message.reply_text(
            f"Legal {self.user['name']}! Agora me diga, você é homem ou mulher?\n\nSe você quiser pular essa etapa, digite /pular.",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="Homem ou Mulher?"
            )
        )

        return GENDER
    
    async def skip_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Skips the name iteration"""
        await update.message.reply_text(
            "Ok, vamos pular essa etapa."
        )
        return GENDER
    
    async def gender(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Stores gender and asks for a photo."""
        logger.info(f"Gender of {self.user['name']}: {update.message.text}")
        self.user["gender"] = update.message.text
        await update.message.reply_text(
            f"Legal! Agora, me envie uma foto sua, {self.user['name']}. \n\nSe você quiser pular essa etapa, digite /pular.",
            reply_markup=ReplyKeyboardRemove(),
        )

        return PHOTO
    
    async def skip_gender(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Skips the gender iteration"""
        await update.message.reply_text(
            "Ok, vamos pular essa etapa."
        )
        return PHOTO
        

    async def photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Stores the photo and asks for a location."""
        print(update)
        photo_file = await update.message.photo[-1].get_file()
        self.user["photo"] = photo_file.file_path
        logger.info("Photo of %s: %s", self.user["name"], self.user["photo"])
        await update.message.reply_text(
            "Obrigado pela foto! Agora, me diga onde você está. Basta compartilhar sua localização comigo!. \n\nSe você quiser pular essa etapa, digite /pular.",
            reply_markup=ReplyKeyboardRemove(),
        )

        return LOCATION
    
    async def skip_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Skips the photo iteration"""
        await update.message.reply_text(
            "Ok, vamos pular essa etapa."
        )
        return LOCATION
    
    async def location(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Stores the location and asks for a bio."""
        self.user["location"] = {
            "latitude": update.message.location.latitude,
            "longitude": update.message.location.longitude,
        }
        logger.info(f"Location of {self.user['name']}: {self.user['location']}")
        await update.message.reply_text(
            "Legal! Por último, me conte um pouco sobre você.",
            reply_markup=ReplyKeyboardRemove(),
        )

        return BIO
    
    async def skip_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Skips the location iteration"""
        await update.message.reply_text(
            "Ok, vamos pular essa etapa."
        )
        return BIO
    
    async def bio(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Stores the bio and ends the conversation."""
        self.user["bio"] = update.message.text
        logger.info("Bio of %s: %s", self.user["name"], self.user["bio"])
        self.user["telegram_id"] = update.message.from_user.id
        self.mongo_client.users.insert_one(self.user)
        await update.message.reply_text(
            "Obrigado por se cadastrar! Aqui estão os detalhes que você me passou:\n"
            f"Nome: {self.user['name']}\n"
            f"Gênero: {self.user['gender']}\n"
            f"Localização: {self.user['location']}\n"
            f"Bio: {self.user['bio']}"
        )
        return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancels and ends the conversation."""
        await update.message.reply_text(
            "Ok, cancelado. Se quiser começar de novo, digite /iniciar."
        )
        return ConversationHandler.END
    
    def get_handler(self) -> ConversationHandler:
        handler = ConversationHandler(
            entry_points=[CommandHandler("iniciar", self.start)],
            states={
                EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.email)],
                NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.name), CommandHandler("pular", self.skip_name)],
                GENDER: [MessageHandler(filters.Regex("^(Homem|Mulher|Outro)$"), self.gender), CommandHandler("pular", self.skip_gender)],
                PHOTO: [MessageHandler(filters.PHOTO, self.photo), CommandHandler("pular", self.skip_photo)],
                LOCATION: [
                    MessageHandler(filters.LOCATION, self.location),
                    MessageHandler("pular", self.location),
                ],
                BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.bio), CommandHandler("pular", self.skip_location)],
            },
            fallbacks=[CommandHandler("cancelar", self.cancel)],
        )
        return handler