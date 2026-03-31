import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai
from google.genai import types
from ddgs import DDGS

# 1. Φορτώνουμε τα κρυφά κλειδιά
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Αρχικοποίηση του νέου Google Gemini Client
client = genai.Client(api_key=GEMINI_API_KEY)

def search_web(query: str) -> str:
    """Ψάχνει στο internet (Web Search) για πρόσφατες ειδήσεις, γεγονότα ή πληροφορίες."""
    print(f"--> [ΣΥΣΤΗΜΑ] Το Gemini ψάχνει στο ίντερνετ για: {query}")
    try:
        # Παίρνουμε τα 3 κορυφαία αποτελέσματα
        results = DDGS().text(query, max_results=3)
        
        if not results:
            return "Δεν βρέθηκαν αποτελέσματα για αυτή την αναζήτηση."
        
        # Ενώνουμε τα αποτελέσματα σε ένα κείμενο για να το διαβάσει το AI
        formatted_results = "Αποτελέσματα Αναζήτησης:\n\n"
        for res in results:
            formatted_results += f"Τίτλος: {res['title']}\nΠερίληψη: {res['body']}\nΠηγή: {res['href']}\n---\n"
            
        return formatted_results
    except Exception as e:
        return f"Υπήρξε σφάλμα κατά την αναζήτηση: {e}"
def get_weather(location: str) -> str:
    """Βρίσκει τον τρέχοντα καιρό για μια συγκεκριμένη τοποθεσία."""
    # Σε ένα πραγματικό σενάριο, εδώ θα καλούσαμε ένα API (π.χ. OpenWeather).
    # Για τώρα, θα βάλουμε μια dummy απάντηση για να δούμε πώς το διαχειρίζεται το AI.
    print(f"--> [ΣΥΣΤΗΜΑ] Το Gemini ζήτησε τον καιρό για: {location}")
    
    if "αθήνα" in location.lower():
        return f"Ο καιρός στην περιοχή {location} είναι ηλιόλουστος με 28 βαθμούς."
    else:
        return f"Ο καιρός στην περιοχή {location} είναι βροχερός με 15 βαθμούς."
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Γεια! Είμαι ο νέος σου AI βοηθός. Στείλε μου ό,τι θέλεις!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    # Δείχνουμε στο Telegram ότι ο bot "πληκτρολογεί..."
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    
    try:
        # Δίνουμε στο Gemini πρόσβαση στη συνάρτησή μας
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_text,
            config=types.GenerateContentConfig(
               tools=[get_weather, search_web], # Εδώ περνάμε τη συνάρτηση!
            )
        )
        bot_reply = response.text
    except Exception as e:
        bot_reply = f"Ουπς, κάτι πήγε λάθος με το Gemini: {e}"

    await update.message.reply_text(bot_reply)

def main():
    print("Εκκίνηση του bot με τα απευθείας κλειδιά...")
    
    # Έλεγχος ότι έβαλες τα κλειδιά
    if "ΒΑΛΕ_ΤΟ_" in TELEGRAM_TOKEN:
        print("ΣΦΑΛΜΑ: Ξέχασες να βάλεις το Telegram Token στον κώδικα!")
        return

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Το Bot ξεκίνησε! Πήγαινε στο Telegram και στείλε του μήνυμα...")
    app.run_polling()

if __name__ == '__main__':
    main()