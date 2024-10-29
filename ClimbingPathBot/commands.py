class Command:
    def __init__(self, command, bot, chat_id):
        self.command = command
        self.bot = bot
        self.chat_id = chat_id
        self._available_commands()
        
    def _available_commands(self):
        self.available_commands = (
            "/start - Inicia o bot",
            "/log - Registre suas cadenas",
            "/help - Mostra os comandos disponíveis"
        )
    
    def get_commands(self):
        return self.available_commands
    
    def start(self):
        text = (
            "Olá! Eu sou o Climbing Path Bot. Como posso te ajudar?",
            "\n".join(self.get_commands())
        )
        return "\n".join(text)

    def help(self):
        return self.start()
        
    def log(self):
        form_text = """Envie sua cadena no formato:
        - Data: dd/mm/aaaa
        - Nome da via: <nome da via>
        - Grau: <grau>
        - Setor: <setor>
        - Pico: <pico>
        - Observações: <observações>
        """
        return form_text
    
    async def run(self, text):
        if text == "/start":
            await self.bot.sendMessage(self.chat_id, self.start())
        elif text == "/help":
            await self.bot.sendMessage(self.chat_id, self.help())
        elif text == "/log":
            await self.bot.sendMessage(self.chat_id, self.log())
        else:
            await self.bot.sendMessage(self.chat_id, "Comando inválido. Envie /help para ver os comandos disponíveis.")