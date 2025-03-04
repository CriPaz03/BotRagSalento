import os
from dotenv import load_dotenv
from telegramServices import TelegramServices

load_dotenv()
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")

def main() -> None:
    TelegramServices(TELEGRAM_TOKEN).start_bot()


if __name__ == "__main__":
    if not TELEGRAM_TOKEN:
        print("Errore: È necessario impostare il token del bot Telegram.")
        exit(1)

    print("Avvio bot...")
    main()
