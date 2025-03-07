import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from ragServices import RagServices


class TelegramServices:
    def __init__(self, token, api_key_elevenlabs, vectorize_api_token):
        self.token = token
        self.rag = RagServices(vectorize_api_token, api_key_elevenlabs)

    def start_bot(self):
        application = Application.builder().token(self.token).build()
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("prompt", self.selected_prompt))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        application.add_handler(CallbackQueryHandler(self.button_callback))
        application.run_polling()

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        prompt_mapping = {
            "default_prompt": (1, "Prompt di default"),
            "prompt2": (2, "Prompt 2"),
            "prompt3": (3, "Prompt 3"),
            "mappa_concettuale": (4, "Mappa concettuale")
        }
        if query.data in prompt_mapping:
            number, name = prompt_mapping[query.data]
            await self.set_prompt(update, context, number, name)


    async def selected_prompt(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        keyboard = [
            [
                InlineKeyboardButton("Prompt Default", callback_data="default_prompt"),
                InlineKeyboardButton("Prompt 2", callback_data="prompt2")
            ],
            [
                InlineKeyboardButton("Prompt 3", callback_data="prompt3"),
                InlineKeyboardButton("Mappa Concettuale", callback_data="mappa_concettuale")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            """Clicca un bottone qui in basso per cambiare il prompt""",
            reply_markup=reply_markup
        )

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        await update.message.reply_text(
            f"""Ciao {user.username}! Sono un bot che risponde alle tue domande sul Salento nel alto-medioevo. Scrivimi una domanda e utilizzerò il sistema RAG per trovare informazioni rilevanti."""
        )

    async def set_prompt(self, update: Update, context: ContextTypes.DEFAULT_TYPE, prompt_number: int,
                         prompt_name: str) -> None:
        self.rag.set_prompt(prompt_number)

        response_text = f"{prompt_name} impostato: {self.rag.get_prompt()}"

        if hasattr(update, 'callback_query') and update.callback_query:
            await update.callback_query.message.reply_text(response_text)
        else:
            await update.message.reply_text(response_text)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            """
Puoi farmi qualsiasi domanda e cercherò di trovare le informazioni più rilevanti sul Salento nel alto-medioevo.
Comandi disponibili:
/start - Avvia il bot
/help - Mostra questo messaggio di aiuto
/prompt - Cambiare prompt
            """
        )


    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        question = update.message.text

        await update.message.reply_text("🔍 Sto cercando informazioni rilevanti...")
        try:
            # Crea una nuova istanza di RagServices per ogni richiesta se necessario per utenti diversi
            # Se hai bisogno di supportare più utenti contemporaneamente, dovresti creare un'istanza per ogni chat_id
            # Esempio: self.rag_instances[update.effective_chat.id] = RagServices()

            llm_response = await self.rag.query_llm_openai(question)

            await update.message.reply_text(llm_response)
            try:
                with open("temp_audio.mp3", "rb") as audio_file:
                    await update.message.reply_voice(audio_file)
                os.remove("temp_audio.mp3")
            except:
                pass

        except Exception as e:
            await update.message.reply_text(f"Errore llm ({e})")