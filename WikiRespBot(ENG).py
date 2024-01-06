##          Эмир Абдуллаев && Resp                                   ##
##          Translator and Wikipedia in the TELEGRAM bot             ##
##          IF YOU ARE TRYING TO PUBLISH, SPECIFY THE AUTHOR!        ##
import telebot
import requests
import wikipedia
from telebot import types
from bs4 import BeautifulSoup
import re
from googletrans import Translator

TOKEN = 'YOUR_API_KEY_TELEGRAM_BOT' # WRITE YOUR TELEGRAM BOT KEY HERE
bot = telebot.TeleBot(TOKEN)

selected_action = ""

## BASIC SETTINGS 
name_project = "WikiRespBot" # THE NAME OF THE BOT
welcome_project = f"Hi! I am {name_project} - your reliable assistant in finding information from Wikipedia and translating text! If you want to translate the text or find the definition of a word, just click on the button at the bottom" # GREETING THE BOT
error_message = "Sorry, I didn't understand your message. You may have forgotten to select an action, to select an action, click on /help." # IF THE COMMAND IS NOT FOUND, THE BOT OUTPUTS THE FOLLOWING.
help_message = "Your current selection was reset automatically if it was made. To select an action again, click on the button at the bottom." # IF A PERSON ENTERS THE /HELP COMMAND, THE BOT RESETS THE CURRENT SELECTION
reset_button_message = "Reset the selection" # RESETS THE SELECTION IF THE PERSON CLICKED ONE ACTION AND THEN ANOTHER.
choice_made = "You have already chosen an action. If you decide to choose another action, please reset this selection using the - /help) and make the choice again." # IF A PERSON HAS CHOSEN TWO CHOICES, THEN THE USER IS NOTIFIED.
## TRANSLATE
translate_button_message = "Translate the text" # BUTTON
enter_text_translate = "Enter the text to translate:" # TEXT
error_wiki_message = "Unfortunately, it was not possible to find information on this term. Try to enter another term." # ERROR IF THE TERM IS NOT FOUND
repeat_enter_text_translate = "Enter the following text to translate (the language you want to translate into remains the same, if you want to change it, enter /help):" # CONTINUATION, IF THE USER DECIDES TO CHOOSE A NEW ACTION, THEN WRITES /HELP
select_the_translation_language = "Select the translation language:" # THE TEXT THE USER WANTS TO TRANSLATE TO

## WIKIPEDIA
api_wikipedia_en = "https://en.wikipedia.org/w/api.php" # API Wikipedia
searchwiki_button_message = "Wikipedia search" # BUTTON
enter_request_wiki = "Enter a search query in Wikipedia:" # TEXT
repeating_enter_request_wiki = "Enter the following Wikipedia search query (if you want to change the selection, enter /help):" # CONTINUATION, IF THE USER DECIDES TO CHOOSE A NEW ACTION, THEN WRITES /HELP
reminder_message = "We are very glad that you have found the necessary information! We noticed that you often use our bot, and we are very pleased. If it's not difficult for you, please leave your feedback about our bot. We will be grateful for any feedback you can provide. With your help, we can improve our bot and make it even more useful for you and other users. Thanks!" # AN ALERT TO RATE THE BOT, AFTER SEVERAL SEARCHES FOR TERMS
## REVIEWS
telegram_project_reviews = "t.me/wikirespbotreviews" # LINK TO REVIEWS
reviews_button_message = "Reviews" # BUTTON
## FEEDBACK
telegram_project_feedback = "t.me/resppl" # LINK TO THE FEEDBACK
feedback_button_message = "Feedback" # BUTTON

searches_count = {}
poll_shown = set()

def get_wikipedia_summary(term):
    url = api_wikipedia_en
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
    
@bot.callback_query_handler(func=lambda call: call.data in ['translate', 'searchwiki'])
def handle_action_button(call):
    global selected_action

    if selected_action and call.data != "reset":
        bot.send_message(call.message.chat.id, choice_made)
    else:
        if call.data == "reset":
            selected_action = ""
            return
        selected_action = call.data
        if selected_action == "translate":
            handle_translate_button(call)
        elif selected_action == "searchwiki":
            handle_searchwiki_button(call)

@bot.callback_query_handler(func=lambda call: call.data == 'translate')
def handle_translate_button(call):
    bot.send_message(call.message.chat.id, select_the_translation_language, reply_markup=generate_translate_markup())

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
    markup.row(telebot.types.InlineKeyboardButton(text="Hungarian", callback_data="hu"),
               telebot.types.InlineKeyboardButton(text="Finnish", callback_data="fi"))
    markup.row(telebot.types.InlineKeyboardButton(text="Azerbaijani", callback_data="az"),
               telebot.types.InlineKeyboardButton(text="Uzbek", callback_data="uz"))
    markup.row(telebot.types.InlineKeyboardButton(text="Kazakh", callback_data="kk"),
               telebot.types.InlineKeyboardButton(text="Belarusian", callback_data="be"))
    return markup


@bot.callback_query_handler(func=lambda call: call.data in ['ru', 'en', 'de', 'fr', 'es', 'ja', 'zh', 'ko', 'ar', 'it', 'pt', 'tr', 'pl', 'sv', 'el', 'cs', 'hu', 'fi', 'az', 'uz', 'kk', 'be'])
def handle_target_language(call):
    target_lang = call.data
    bot.send_message(call.message.chat.id, enter_text_translate)
    bot.register_next_step_handler(call.message, translate_text, target_lang)

def translate_text(message, target_lang):
    if message.text == '/help':
        global selected_action
        selected_action = ""
        markup = telebot.types.InlineKeyboardMarkup()
        translate = telebot.types.InlineKeyboardButton(translate_button_message, callback_data='translate')
        searchwiki = telebot.types.InlineKeyboardButton(searchwiki_button_message, callback_data="searchwiki")
        reviewcheck = telebot.types.InlineKeyboardButton(reviews_button_message, url=telegram_project_reviews)
        feedback = telebot.types.InlineKeyboardButton(feedback_button_message, url=telegram_project_feedback)
        markup.row(translate, searchwiki)
        markup.row(reviewcheck, feedback)
        bot.send_message(message.chat.id, help_message, reply_markup=markup)
        return
    text = message.text
    translator = Translator()
    translation = translator.translate(text, dest=target_lang).text
    bot.send_message(message.chat.id, translation)
    bot.send_message(message.chat.id, repeat_enter_text_translate)
    bot.register_next_step_handler(message, translate_text, target_lang)

@bot.callback_query_handler(func=lambda call: call.data == 'searchwiki')
def handle_searchwiki_button(call):
    bot.send_message(call.message.chat.id, enter_request_wiki)
    bot.register_next_step_handler(call.message, search_wikipedia)

def search_wikipedia(message):
    if message.text == '/help':
        global selected_action
        selected_action = ""
        markup = telebot.types.InlineKeyboardMarkup()
        translate = telebot.types.InlineKeyboardButton(translate_button_message, callback_data='translate')
        searchwiki = telebot.types.InlineKeyboardButton(searchwiki_button_message, callback_data="searchwiki")
        reviewcheck = telebot.types.InlineKeyboardButton(reviews_button_message, url=telegram_project_reviews)
        feedback = telebot.types.InlineKeyboardButton(feedback_button_message, url=telegram_project_feedback)
        markup.row(translate, searchwiki)
        markup.row(reviewcheck, feedback)
        bot.send_message(message.chat.id, help_message, reply_markup=markup)
        return
    else:
        term = message.text.lower()
        summary, image_url = get_wikipedia_summary(term)
        if summary:
            bot.send_message(message.chat.id, summary)
            if image_url:
                bot.send_photo(message.chat.id, image_url)
        else:
            bot.send_message(message.chat.id, error_wiki_message)

        bot.send_message(message.chat.id, repeating_enter_request_wiki)
        bot.register_next_step_handler(message, search_wikipedia)

    user_id = message.chat.id
    if user_id not in poll_shown:
        search_count = searches_count.get(user_id, 0)
        search_count += 1
        searches_count[user_id] = search_count

        if search_count == 5:
            markup = telebot.types.InlineKeyboardMarkup()
            reviewcheck = telebot.types.InlineKeyboardButton(reviews_button_message, url=telegram_project_reviews)
            feedback = telebot.types.InlineKeyboardButton(feedback_button_message, url=telegram_project_feedback)
            markup.row(reviewcheck, feedback)
            bot.send_message(user_id, reminder_message, reply_markup=markup)
            poll_shown.add(user_id)
            searches_count[user_id] = 0

@bot.message_handler(commands=['help'])
def handle_start(message):
    global selected_action
    selected_action = ""
    markup = telebot.types.InlineKeyboardMarkup()
    translate = telebot.types.InlineKeyboardButton(translate_button_message, callback_data='translate')
    searchwiki = telebot.types.InlineKeyboardButton(searchwiki_button_message, callback_data="searchwiki")
    reviewcheck = telebot.types.InlineKeyboardButton(reviews_button_message, url=telegram_project_reviews)
    feedback = telebot.types.InlineKeyboardButton(feedback_button_message, url=telegram_project_feedback)
    markup.row(translate, searchwiki)
    markup.row(reviewcheck, feedback)
    bot.send_message(message.chat.id, help_message, reply_markup=markup)
    return

@bot.message_handler(commands=['start'])
def handle_start(message):
    global selected_action
    markup = telebot.types.InlineKeyboardMarkup()
    translate = telebot.types.InlineKeyboardButton(translate_button_message, callback_data='translate')
    searchwiki = telebot.types.InlineKeyboardButton(searchwiki_button_message, callback_data="searchwiki")
    reviewcheck = telebot.types.InlineKeyboardButton(reviews_button_message, url=telegram_project_reviews)
    feedback = telebot.types.InlineKeyboardButton(feedback_button_message, url=telegram_project_feedback)
    markup.row(translate, searchwiki)
    markup.row(reviewcheck, feedback)
    bot.send_message(message.chat.id, welcome_project, reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    bot.send_message(message.chat.id, error_message)
bot.polling()
