##          Эмир Абдуллаев && Resp                                   ##
##          Переводчик и Википедия в TELEGRAM-боте                   ##
##          ЕСЛИ ВЫ ПЫТАЕТЕСЬ ОПУБЛИКОВАТЬ, УКАЖИТЕ АВТОРА!          ##
import telebot
import requests
import wikipedia
from bs4 import BeautifulSoup
import re
from googletrans import Translator

TOKEN = 'YOUR_API_KEY_TELEGRAM_BOT' # НАПИШИТЕ ЗДЕСЬ СВОЮ КЛЮЧ ОТ TELEGRAM-БОТА
bot = telebot.TeleBot(TOKEN)

name_project = "WikiRespBot" # НАПИШИТЕ ЗДЕСЬ ИМЯ СВОЕГО БОТА
telegram_project_reviews = "t.me/wikirespbotreviews" # ОСТАВЬТЕ ССЫЛКУ, ГДЕ НАХОДЯТСЯ ОТЗЫВЫ
telegram_project_feedback = "t.me/resppl" # ОСТАВЬТЕ ССЫЛКУ, ГДЕ МОЖНО ОСТАВИТЬ ОБРАТНУЮ СВЯЗЬ

searches_count = {}
poll_shown = set()

def get_wikipedia_summary(term):
    url = "https://ru.wikipedia.org/w/api.php"
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
    bot.send_message(call.message.chat.id, "Выберите язык перевода:", reply_markup=generate_translate_markup())

def generate_translate_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(telebot.types.InlineKeyboardButton(text="Русский", callback_data="ru"),
              telebot.types.InlineKeyboardButton(text="Английский", callback_data="en"))
    markup.row(telebot.types.InlineKeyboardButton(text="Немецкий", callback_data="de"),
              telebot.types.InlineKeyboardButton(text="Французский", callback_data="fr"))
    markup.row(telebot.types.InlineKeyboardButton(text="Испанский", callback_data="es"),
               telebot.types.InlineKeyboardButton(text="Японский", callback_data="ja"))
    markup.row(telebot.types.InlineKeyboardButton(text="Китайский", callback_data="zh"),
               telebot.types.InlineKeyboardButton(text="Корейский", callback_data="ko"))
    markup.row(telebot.types.InlineKeyboardButton(text="Арабский", callback_data="ar"),
               telebot.types.InlineKeyboardButton(text="Итальянский", callback_data="it"))
    markup.row(telebot.types.InlineKeyboardButton(text="Португальский", callback_data="pt"),
               telebot.types.InlineKeyboardButton(text="Турецкий", callback_data="tr"))
    markup.row(telebot.types.InlineKeyboardButton(text="Польский", callback_data="pl"),
               telebot.types.InlineKeyboardButton(text="Шведский", callback_data="sv"))
    markup.row(telebot.types.InlineKeyboardButton(text="Греческий", callback_data="el"),
               telebot.types.InlineKeyboardButton(text="Чешский", callback_data="cs"))
    markup.row(telebot.types.InlineKeyboardButton(text="Венгерский", callback_data="hu"),
               telebot.types.InlineKeyboardButton(text="Финский", callback_data="fi"))
    markup.row(telebot.types.InlineKeyboardButton(text="Азербайджанский", callback_data="az"),
               telebot.types.InlineKeyboardButton(text="Узбекский", callback_data="uz"))
    markup.row(telebot.types.InlineKeyboardButton(text="Казахский", callback_data="kk"),
               telebot.types.InlineKeyboardButton(text="Белорусский", callback_data="be"))
    return markup


@bot.callback_query_handler(func=lambda call: call.data in ['ru', 'en', 'de', 'fr', 'es', 'ja', 'zh', 'ko', 'ar', 'it', 'pt', 'tr', 'pl', 'sv', 'el', 'cs', 'hu', 'fi', 'az', 'uz', 'kk', 'be'])
def handle_language_button(call):
    bot.send_message(call.message.chat.id, "Введите текст для перевода:")
    bot.register_next_step_handler(call.message, translate_text, call.data)

def translate_text(message, target_lang):
    text = message.text
    translator = Translator()
    translation = translator.translate(text, dest=target_lang).text
    bot.send_message(message.chat.id, translation)
    markup = telebot.types.InlineKeyboardMarkup()
    translate = telebot.types.InlineKeyboardButton(text="Перевести текст", callback_data='translate')
    searchwiki = telebot.types.InlineKeyboardButton(text="Поиск по Википедии", callback_data="searchwiki")
    reviewcheck = telebot.types.InlineKeyboardButton(text="Отзывы", url=telegram_project_reviews)
    feedback = telebot.types.InlineKeyboardButton(text="Обратная связь", url=telegram_project_feedback)
    markup.row(translate, searchwiki)
    markup.row(reviewcheck, feedback)
    bot.send_message(message.chat.id, "Ваш выбор был сброшен автоматически. Чтобы снова выбрать действие, нажмите на кнопку внизу.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'searchwiki')
def handle_searchwiki_button(call):
    bot.send_message(call.message.chat.id, "Введите поисковый запрос в Википедии:")
    bot.register_next_step_handler(call.message, search_wikipedia)
def search_wikipedia(message):
    term = message.text.lower()
    summary, image_url = get_wikipedia_summary(term)
    if summary:
        bot.send_message(message.chat.id, summary)
        if image_url:
            bot.send_photo(message.chat.id, image_url)
    else:
        bot.send_message(message.chat.id, "К сожалению, найти информацию по этому термину не удалось. Попробуйте ввести другой термин")
    user_id = message.chat.id
    if user_id not in poll_shown:
        search_count = searches_count.get(user_id, 0)
        search_count += 1
        searches_count[user_id] = search_count

        if search_count == 5:
            markup = telebot.types.InlineKeyboardMarkup()
            reviewcheck = telebot.types.InlineKeyboardButton(text="Оставить отзыв", url=telegram_project_reviews)
            feedback = telebot.types.InlineKeyboardButton(text="Обратная связь", url=telegram_project_feedback)
            markup.row(reviewcheck, feedback)
            bot.send_message(user_id, "Мы очень рады, что вы нашли необходимую информацию! Мы заметили, что вы часто пользуетесь нашим ботом, и нам это очень приятно. Если вам не сложно, пожалуйста, оставьте свой отзыв о нашем боте. Мы будем благодарны за любой отзыв, который вы сможете предоставить. С вашей помощью мы сможем улучшить нашего бота и сделать его еще более полезным для вас и других пользователей. Спасибо!", reply_markup=markup)
            poll_shown.add(user_id)
            searches_count[user_id] = 0
    markup = telebot.types.InlineKeyboardMarkup()
    translate = telebot.types.InlineKeyboardButton(text="Перевести текст", callback_data='translate')
    searchwiki = telebot.types.InlineKeyboardButton(text="Поиск по Википедии", callback_data="searchwiki")
    reviewcheck = telebot.types.InlineKeyboardButton(text="Отзывы", url=telegram_project_reviews)
    feedback = telebot.types.InlineKeyboardButton(text="Обратная связь", url=telegram_project_feedback)
    markup.row(translate, searchwiki)
    markup.row(reviewcheck, feedback)
    bot.send_message(message.chat.id, "Ваш выбор был сброшен автоматически. Чтобы снова выбрать действие, нажмите на кнопку внизу.", reply_markup=markup)

@bot.message_handler(commands=['help'])
def handle_start(message):
    markup = telebot.types.InlineKeyboardMarkup()
    translate = telebot.types.InlineKeyboardButton(text="Перевести текст", callback_data='translate')
    searchwiki = telebot.types.InlineKeyboardButton(text="Поиск по Википедии", callback_data="searchwiki")
    reviewcheck = telebot.types.InlineKeyboardButton(text="Отзывы", url=telegram_project_reviews)
    feedback = telebot.types.InlineKeyboardButton(text="Обратная связь", url=telegram_project_feedback)
    markup.row(translate, searchwiki)
    markup.row(reviewcheck, feedback)
    bot.send_message(message.chat.id, "Ваш выбор был сброшен автоматически. Чтобы снова выбрать действие, нажмите на кнопку внизу.", reply_markup=markup)


@bot.message_handler(commands=['start'])
def handle_start(message):
    markup = telebot.types.InlineKeyboardMarkup()
    translate = telebot.types.InlineKeyboardButton(text="Перевести текст", callback_data='translate')
    searchwiki = telebot.types.InlineKeyboardButton(text="Поиск по Википедии", callback_data="searchwiki")
    reviewcheck = telebot.types.InlineKeyboardButton(text="Отзывы", url=telegram_project_reviews)
    feedback = telebot.types.InlineKeyboardButton(text="Обратная связь", url=telegram_project_feedback)
    markup.row(translate, searchwiki)
    markup.row(reviewcheck, feedback)
    bot.send_message(message.chat.id, f"Привет! Я {name_project} - ваш надежный помощник в поиске информации из Википедии и переводе текста! Если вы хотите перевести текст или найти определение слова, просто нажмите на кнопку внизу.", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    bot.send_message(message.chat.id, "Извините, я не понял вашего сообщения. Возможно, вы забыли выбрать действие, чтобы выбрать действие, нажмите на /help.")
bot.polling()