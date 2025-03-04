from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from ragServices import RagServices


class TelegramServices:

    rag = RagServices()
    def __init__(self, token):
        self.token = token

    def start_bot(self):
        application = Application.builder().token(self.token).build()
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("DefaultPrompt", self.set_prompt_default))
        application.add_handler(CommandHandler("prompt1", self.set_prompt_1))
        application.add_handler(CommandHandler("prompt2", self.set_prompt_2))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        application.run_polling()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        await update.message.reply_text(
            f"""Ciao {user.username}! Sono un bot che risponde alle tue domande sul Salento nel alto-medioevo.Scrivimi una domanda e utilizzerò il sistema RAG per trovare informazioni rilevanti."""
        )

    async def set_prompt_1(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.rag.set_prompt(1)
        await update.message.reply_text(f"Prompt 1 impostato: {self.rag.get_prompt()}")

    async def set_prompt_2(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.rag.set_prompt(2)
        await update.message.reply_text(f"Prompt 2 impostato: {self.rag.get_prompt()}")

    async def set_prompt_default(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.rag.set_prompt(9999)
        await update.message.reply_text(f"Prompt di default impostato: {self.rag.get_prompt()}")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            """
Puoi farmi qualsiasi domanda e cercherò di trovare le informazioni più rilevanti sul Salento nel alto-medioevo.
Comandi disponibili:
/start - Avvia il bot
/help - Mostra questo messaggio di aiuto
/defaultPrompt - Prompt di default impostato
/prompt1 - Prompt 1 impostato
/prompt2 - Prompt 2 impostato
            """
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        question = update.message.text

        await update.message.reply_text("🔍 Sto cercando informazioni rilevanti...")
        try:
            llm_response = await self.rag.query_llm_llama(question)
            await update.message.reply_text(llm_response)
        except Exception as e:
            await update.message.reply_text(f"Errore llm ({e})")

