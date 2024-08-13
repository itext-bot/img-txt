import logging
import pytesseract
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from PIL import Image
import requests
from io import BytesIO
import os
import uuid

# Bot token and channel username
TOKEN = '7489650180:AAEwdN6p4J-DZch7GpRhGVHGU2kUe_IZnrs'
CHANNEL_USERNAME = '@ethixcyber'

# Initialize logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Supported languages
SUPPORTED_LANGUAGES = {
    'eng': 'English', 'urd': 'Urdu', 'ara': 'Arabic',
    'fra': 'French', 'spa': 'Spanish', 'deu': 'German',
    'ita': 'Italian', 'por': 'Portuguese', 'nld': 'Dutch',
    'rus': 'Russian', 'chi_sim': 'Chinese Simplified', 'chi_tra': 'Chinese Traditional',
    'jpn': 'Japanese', 'kor': 'Korean', 'hin': 'Hindi',
    'ben': 'Bengali', 'tam': 'Tamil', 'tel': 'Telugu',
    'fas': 'Persian', 'tur': 'Turkish', 'ell': 'Greek',
    'heb': 'Hebrew', 'vie': 'Vietnamese', 'tha': 'Thai',
    'msa': 'Malay', 'swa': 'Swahili', 'ind': 'Indonesian',
    'pol': 'Polish', 'ces': 'Czech', 'ron': 'Romanian',
    'hun': 'Hungarian'
}

# Welcome message
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Check Subscription", callback_data='check_subscription')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Welcome to imgtotxt Bot!\nCreated by Haider Kamran.\n\n"
        "This bot extracts text from images in various languages. 🌍\n\n"
        "To get started, please follow our channel: https://t.me/ethixcyber\n\n"
        "Once subscribed, you can upload an image, select the language, and receive the extracted text.",
        reply_markup=reply_markup
    )

# Check subscription
async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    # API request to get the user's status in the channel
    try:
        response = requests.get(f'https://api.telegram.org/bot{TOKEN}/getChatMember?chat_id={CHANNEL_USERNAME}&user_id={user_id}')
        data = response.json()
        
        if response.status_code != 200 or 'result' not in data:
            raise Exception(f"Unexpected response: {data}")
        
        status = data['result'].get('status', '')

        if status in ['member', 'administrator', 'creator']:
            keyboard = [
                [InlineKeyboardButton("Share Bot", url='https://t.me/share/url?url=https://t.me/your_bot_username&text=Check%20out%20this%20amazing%20bot%20that%20extracts%20text%20from%20images%20in%20multiple%20languages!%20Follow%20the%20channel%20and%20start%20using%20it%20now!')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "🎉 Congratulations! You're subscribed to our channel! 🎉\n\n"
                "Thank you for your support! 🙏\n\nPlease upload an image for text extraction.",
                reply_markup=reply_markup
            )
        else:
            await query.edit_message_text(
                "You're not subscribed to the channel. Please subscribe first: https://t.me/ethixcyber",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Check Subscription Again", callback_data='check_subscription')]])
            )
    
    except requests.exceptions.RequestException as e:
        await query.edit_message_text(f"Network error occurred: {str(e)}")
    except Exception as e:
        await query.edit_message_text(
            "An error occurred while checking your subscription. "
            "Please make sure the bot is an admin in the channel and try again."
        )

# Handle image messages
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        # Get the highest quality photo
        photo = update.message.photo[-1]
        file = await photo.get_file()
        
        # Download file as byte array
        image_bytes = await file.download_as_bytearray()
        
        # Generate a unique filename
        unique_filename = f'image_{uuid.uuid4()}.png'
        
        # Open image from byte array
        img = Image.open(BytesIO(image_bytes))
        
        # Save image temporarily
        img.save(unique_filename)
        
        # Ask for language selection
        keyboard = [
            [InlineKeyboardButton("English", callback_data='eng'),
             InlineKeyboardButton("Urdu", callback_data='urd'),
             InlineKeyboardButton("Arabic", callback_data='ara')],
            [InlineKeyboardButton("French", callback_data='fra'),
             InlineKeyboardButton("Spanish", callback_data='spa'),
             InlineKeyboardButton("German", callback_data='deu')],
            [InlineKeyboardButton("Italian", callback_data='ita'),
             InlineKeyboardButton("Portuguese", callback_data='por'),
             InlineKeyboardButton("Dutch", callback_data='nld')],
            [InlineKeyboardButton("Russian", callback_data='rus'),
             InlineKeyboardButton("Chinese Simplified", callback_data='chi_sim'),
             InlineKeyboardButton("Chinese Traditional", callback_data='chi_tra')],
            [InlineKeyboardButton("Japanese", callback_data='jpn'),
             InlineKeyboardButton("Korean", callback_data='kor'),
             InlineKeyboardButton("Hindi", callback_data='hin')],
            [InlineKeyboardButton("Bengali", callback_data='ben'),
             InlineKeyboardButton("Tamil", callback_data='tam'),
             InlineKeyboardButton("Telugu", callback_data='tel')],
            [InlineKeyboardButton("Persian", callback_data='fas'),
             InlineKeyboardButton("Turkish", callback_data='tur'),
             InlineKeyboardButton("Greek", callback_data='ell')],
            [InlineKeyboardButton("Hebrew", callback_data='heb'),
             InlineKeyboardButton("Vietnamese", callback_data='vie'),
             InlineKeyboardButton("Thai", callback_data='tha')],
            [InlineKeyboardButton("Malay", callback_data='msa'),
             InlineKeyboardButton("Swahili", callback_data='swa'),
             InlineKeyboardButton("Indonesian", callback_data='ind')],
            [InlineKeyboardButton("Polish", callback_data='pol'),
             InlineKeyboardButton("Czech", callback_data='ces'),
             InlineKeyboardButton("Romanian", callback_data='ron')],
            [InlineKeyboardButton("Hungarian", callback_data='hun')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Select the language for text extraction:', reply_markup=reply_markup)
        
        # Store the unique filename in context for later use
        context.chat_data['image_filename'] = unique_filename

# Extract text based on selected language
async def extract_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = query.data

    # Retrieve the unique filename from context
    filename = context.chat_data.get('image_filename')
    
    if not filename:
        await query.message.reply_text("No image found. Please upload an image first.")
        return
    
    if lang not in SUPPORTED_LANGUAGES:
        await query.message.reply_text(
            "❌ Invalid language selection. Please select a valid language from the options provided."
        )
        return

    # Verify language files exist
    if not os.path.isfile(f'/usr/share/tesseract-ocr/5/tessdata/{lang}.traineddata'):
        await query.message.reply_text(f"❌ Language '{lang}' is not supported by Tesseract.")
        return

    try:
        img = Image.open(filename)
        text = pytesseract.image_to_string(img, lang=lang)
        
        # Delete the image file after processing
        os.remove(filename)
        
        # Reply with the extracted text
        await query.message.reply_text(f"Extracted Text:\n\n{text}")
        await query.answer()  # Acknowledge the callback
    except Exception as e:
        await query.message.reply_text(f"Failed to extract text: {str(e)}")

# Main function to run the bot
def main():
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(check_subscription, pattern='check_subscription'))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    application.add_handler(CallbackQueryHandler(extract_text, pattern='^(eng|urd|ara|fra|spa|deu|ita|por|nld|rus|chi_sim|chi_tra|jpn|kor|hin|ben|tam|tel|fas|tur|ell|heb|vie|tha|msa|swa|ind|pol|ces|ron|hun)$'))
    
    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
