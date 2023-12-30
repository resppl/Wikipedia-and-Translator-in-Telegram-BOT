##          Emir Abdullaev && Resp                                   ##
##          Translator & Wikipedia in TELEGRAM BOT                   ##
##          IF YOU'RE TRYIN' TO STEL, SPECIFY THE AUTHOR!            ##
import telebot
import requests
import wikipedia
from bs4 import BeautifulSoup
import re
from googletrans import Translator

TOKEN = 'YOUR_API_KEY_TELEGRAM_BOT' # WRITE HERE YOUR KEY TO THE TELEGRAM BOT
bot = telebot.TeleBot(TOKEN)

name_project = "WikiRespBot" # BOT NAME
telegram_project_reviews = "t.me/wikirespbotreviews" # TELEGRAM PROJECT REVIEWS
telegram_project_feedback = "t.me/resppl" # TELEGRAM PROJECT FEEDBACK

searches_count = {}
poll_shown = set()

def get_wikipedia_summary(term):
    url = "https://en.wikipedia.org/w/api.php" # connect wikipedia API key
    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts|pageimages",
        "exintro": True,
        "explaintext": True,
        "titles": term,
        "pithumbsize": 512
    }
    response = requests.get(url, params=params)
    data = response.json()

    page_id = list(data['query']['pages'].keys())[0]
    page = data['query']['pages'].get(page_id)
    if page:
        summary = page.get('extract')
        image_url = page['thumbnail']['source'] if 'thumbnail' in page else None

        if summary:
            clean_summary = summary.strip()
        else:
            clean_summary = None

        return clean_summary, image_url
    else:
        return None, None
    
@bot.callback_query_handler(func=lambda call: call.data == 'translate')
def handle_translate_button(call):
    bot.send_message(call.message.chat.id, "Select translation language:", reply_markup=generate_translate_markup())

def generate_translate_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(telebot.types.InlineKeyboardButton(text="Russian", callback_data="ru"),
              telebot.types.InlineKeyboardButton(text="English", callback_data="en"))
    markup.row(telebot.types.InlineKeyboardButton(text="German", callback_data="de"),
              telebot.types.InlineKeyboardButton(text="French", callback_data="fr"))
    markup.row(telebot.types.InlineKeyboardButton(text="Spanish", callback_data="es"),
               telebot.types.InlineKeyboardButton(text="Japanese", callback_data="ja"))
    markup.row(telebot.types.InlineKeyboardButton(text="Chinese", callback_data="zh"),
               telebot.types.InlineKeyboardButton(text="Korean", callback_data="ko"))
    markup.row(telebot.types.InlineKeyboardButton(text="Arabic", callback_data="ar"),
               telebot.types.InlineKeyboardButton(text="Italian", callback_data="it"))
    markup.row(telebot.types.InlineKeyboardButton(text="Portuguese", callback_data="pt"),
               telebot.types.InlineKeyboardButton(text="Turkish", callback_data="tr"))
    markup.row(telebot.types.InlineKeyboardButton(text="Polish", callback_data="pl"),
               telebot.types.InlineKeyboardButton(text="Swedish", callback_data="sv"))
    markup.row(telebot.types.InlineKeyboardButton(text="Greek", callback_data="el"),
               telebot.types.InlineKeyboardButton(text="Czech", callback_data="cs"))
    markup.row(telebot.types.InlineKeyboardButton(text="Hungarin", callback_data="hu"),
               telebot.types.InlineKeyboardButton(text="Finnish", callback_data="fi"))
    markup.row(telebot.types.InlineKeyboardButton(text="Azerbaijani", callback_data="az"),
               telebot.types.InlineKeyboardButton(text="Uzbek", callback_data="uz"))
    markup.row(telebot.types.InlineKeyboardButton(text="Kazakh", callback_data="kk"),
               telebot.types.InlineKeyboardButton(text="Belarusian", callback_data="be"))
    return markup


@bot.callback_query_handler(func=lambda call: call.data in ['ru', 'en', 'de', 'fr', 'es', 'ja', 'zh', 'ko', 'ar', 'it', 'pt', 'tr', 'pl', 'sv', 'el', 'cs', 'hu', 'fi', 'az', 'uz', 'kk', 'be'])
def handle_language_button(call):
    bot.send_message(call.message.chat.id, "Enter text to translate:")
    bot.register_next_step_handler(call.message, translate_text, call.data)

def translate_text(message, target_lang):
    text = message.text
    translator = Translator()
    translation = translator.translate(text, dest=target_lang).text
    bot.send_message(message.chat.id, translation)
    markup = telebot.types.InlineKeyboardMarkup()
    translate = telebot.types.InlineKeyboardButton(text="Translate a text", callback_data='translate')
    searchwiki = telebot.types.InlineKeyboardButton(text="Search on Wikipedia", callback_data="searchwiki")
    reviewcheck = telebot.types.InlineKeyboardButton(text="Reviews", url=telegram_project_reviews)
    feedback = telebot.types.InlineKeyboardButton(text="Feedback", url=telegram_project_feedback)
    markup.row(translate, searchwiki)
    markup.row(reviewcheck, feedback)
    bot.send_message(message.chat.id, "Your selection was reset automatically. To select an action again, click on the button at the bottom.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'searchwiki')
def handle_searchwiki_button(call):
    bot.send_message(call.message.chat.id, "Enter a search term on Wikipedia:")
    bot.register_next_step_handler(call.message, search_wikipedia)
def search_wikipedia(message):
    term = message.text.lower()
    summary, image_url = get_wikipedia_summary(term)
    if summary:
        bot.send_message(message.chat.id, summary)
        if image_url:
            bot.send_photo(message.chat.id, image_url)
    else:
        bot.send_message(message.chat.id, "Unfortunately, it was not possible to find information on this term. Try to enter another term")
    user_id = message.chat.id
    if user_id not in poll_shown:
        search_count = searches_count.get(user_id, 0)
        search_count += 1
        searches_count[user_id] = search_count

        if search_count == 5:
            markup = telebot.types.InlineKeyboardMarkup()
            reviewcheck = telebot.types.InlineKeyboardButton(text="Leave a review", url=telegram_project_reviews)
            feedback = telebot.types.InlineKeyboardButton(text="Feedback", url=telegram_project_feedback)
            markup.row(reviewcheck, feedback)
            bot.send_message(user_id, "We are very glad that you have found the necessary information! We noticed that you often use our bot, and it is very pleasant for us. If it's not difficult for you, please leave your feedback about our bot. We will be grateful for any feedback you can provide. With your help, we will be able to improve our bot and make it even more useful for you and other users. Thanks!", reply_markup=markup)
            poll_shown.add(user_id)
            searches_count[user_id] = 0
    markup = telebot.types.InlineKeyboardMarkup()
    translate = telebot.types.InlineKeyboardButton(text="Translate a text", callback_data='translate')
    searchwiki = telebot.types.InlineKeyboardButton(text="Search on Wikipedia", callback_data="searchwiki")
    reviewcheck = telebot.types.InlineKeyboardButton(text="Reviews", url=telegram_project_reviews)
    feedback = telebot.types.InlineKeyboardButton(text="Feedback", url=telegram_project_feedback)
    markup.row(translate, searchwiki)
    markup.row(reviewcheck, feedback)
    bot.send_message(message.chat.id, "Your selection was reset automatically. To select an action again, click on the button at the bottom.", reply_markup=markup)

@bot.message_handler(commands=['help'])
def handle_start(message):
    markup = telebot.types.InlineKeyboardMarkup()
    translate = telebot.types.InlineKeyboardButton(text="Translate a text", callback_data='translate')
    searchwiki = telebot.types.InlineKeyboardButton(text="Search on Wikipedia", callback_data="searchwiki")
    reviewcheck = telebot.types.InlineKeyboardButton(text="Reviews", url=telegram_project_reviews)
    feedback = telebot.types.InlineKeyboardButton(text="Feedback", url=telegram_project_feedback)
    markup.row(translate, searchwiki)
    markup.row(reviewcheck, feedback)
    bot.send_message(message.chat.id, "If you want to translate a text or find the definition of a word, just click on the button at the bottom.", reply_markup=markup)


@bot.message_handler(commands=['start'])
def handle_start(message):
    markup = telebot.types.InlineKeyboardMarkup()
    translate = telebot.types.InlineKeyboardButton(text="Translate a text", callback_data='translate')
    searchwiki = telebot.types.InlineKeyboardButton(text="Search on Wikipedia", callback_data="searchwiki")
    reviewcheck = telebot.types.InlineKeyboardButton(text="Reviews", url=telegram_project_reviews)
    feedback = telebot.types.InlineKeyboardButton(text="Feedback", url=telegram_project_feedback)
    markup.row(translate, searchwiki)
    markup.row(reviewcheck, feedback)
    bot.send_message(message.chat.id, f"Hi! I am {name_project} - your reliable assistant for searching information from Wikipedia and translating text! If you want to translate a text or find a definition of a word, just click on the button at the bottom.", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    bot.send_message(message.chat.id, "I'm sorry, I don't understand your message. You may have forgotten to select an action, to select an action, click on /help.")
bot.polling()