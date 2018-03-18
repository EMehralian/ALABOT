# TOKEN = "564808836:AAG_QoeMiclCT5U7TC7eHd2TcFkn21tk6FU"
# TOKEN = "507882226:AAHpSyFVLfgMyEpMLP_bxJUmkKa5rgdYsBQ"
import telegram

TOKEN = "560642035:AAGO1DmK_bUB9aSd5iUgaGfxuDzTv_kHHrQ"
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
import logging
import json
import random
from telegram.error import (TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class User:
    def __init__(self, **entries):
        self.state = "start"
        self.seen = []
        self.submited = []
        self.approved = []
        self.current_problem = ""
        self.pid = 0
        if entries:
            self.__dict__.update(entries)
            # state is one of this: start, challenge, game_state, thinking, waiting_upload, send_message


def start(bot, update):
    chat_id = update.message.chat.id
    if str(chat_id) not in user_dict:
        user = User()
        user_dict[str(chat_id)] = user
        # todo ask student_number
        print(user_dict)
        print("*******************************************************************************************")
    user = user_dict[str(chat_id)]
    user.state = "start"
    if chat_id not in admins:
        reply_keyboard = [['مسابقه عید', 'امکانات دیگر'], ['درباره ما', 'پیشنهادات و انتقادات']]
    else:
        reply_keyboard = [['مسابقه عید', 'امکانات دیگر'], ['درباره ما', 'پیشنهادات و انتقادات'], ['پاسخ به سوالات']]
    text = 'به نام خدا' + "\n" + 'شما در حال استفاده از ربات درس جبر خطی دانشکده مهندسی کامپیوتر دانشگاه صنعتی هستید!' + \
           "\n" + "آدرس کانال درس: @ceit_linear_algebra "
    update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    write_json()


def update_handler(bot, update):
    if update.message:
        chat_id = update.message.chat.id
        user = user_dict[str(chat_id)]

        if user.state == "start":
            if update.message.text:
                if update.message.text == "مسابقه عید":
                    user.state = "challenge"
                if update.message.text == "درباره ما":
                    update.message.reply_text(
                        'این بات توسط تیم تدریسیاری و با همکاری آقای سمیعی پاقعله نوشته شده است! ')
                if update.message.text == 'امکانات دیگر':
                    update.message.reply_text(
                        'به زودی امکانات دیگری از جمله امکان دریافت تمرین ها به این ربات اضافه خواهد شد')
                if update.message.text == 'پیشنهادات و انتقادات':
                    update.message.reply_text('لطفا پیشنهاد و یا انتقاد خود را بنویسید')
                    user.state = "send_suggestions"
        elif user.state == "challenge":
            if update.message.text:
                if update.message.text == "توضیحات":
                    bot.send_document(chat_id, document=open('./ChallengeDescription.pdf', 'rb'))
                    user.state = "challenge"
                if update.message.text == "شرکت در مسابقه":
                    user.state = "game_state"
                if update.message.text == "بازگشت":
                    user.state = "start"
        elif user.state == "game_state":
            if update.message.text:
                if update.message.text == "سوال فعلی":
                    update.message.reply_text(
                        'شما هم اکنون مشغول فکر کردن بر روی سوال' + str(user.current_problem) + 'هستید' + '\n'
                        + ' برای دریافت سوال جدید یا پاسخ این سوال را آپلود کنید و  یا از پاسخ به آن انصراف دهید.')
                    user.state = "thinking"
                if update.message.text == "دریافت سوال جدید":
                    if len(user.seen) >= len(problem_list):
                        update.message.reply_text('فعلا سوال جدیدی وجود ندارد. منتظر سوالات جدید ما باشید!')
                        user.state = "game_state"
                    else:
                        try:
                            # todo #importat " اکسپشن میخوره ولی باز فایل ارسال میشه وجز سوالات فرد محاسبه نمیشه"
                            random_question = random.choice(list(set(problem_list) ^ set(user.seen)))
                            bot.send_document(chat_id, document=open('./problems/' + random_question, 'rb'))
                            user.current_problem = random_question
                            user.seen.append(random_question)
                            user.state = "thinking"
                        except:
                            update.message.reply_text("به علت خطا در شبکه، لطفا مجددا تلاش کنید")
                if update.message.text == "وضعیت سوال‌ها":
                    user.state = "game_state"
                    text = "\n".join(user.seen)
                    update.message.reply_text("سوالات مشاهده شده توسط شما: \n" + text)
                    text = "\n".join(user.approved)
                    update.message.reply_text("سوالات با پاسخ صحیح : \n" + text)
                    if user.current_problem:
                        update.message.reply_text("\n" + "سوالی که هم اکنون برای شما فعال است:" + user.current_problem)
                if update.message.text == "درخواست کمک از تدریسیاران":
                    update.message.reply_text('لطفا سوال خود را بفرمایید!')
                    user.state = "send_message"

                if update.message.text == "جدول امتیازات":
                    update.message.reply_text("به زودی جدول امتیازات به روز رسانی خواهد شد و از این طریق قابل دسترسی است")
                    user.state = "game_state"
                # TODO جدول امتیازات
                if update.message.text == "بازگشت":
                    user.state = "challenge"
        elif user.state == "thinking":
            if update.message.text:
                if update.message.text:
                    if update.message.text == "ارسال پاسخ":
                        update.message.reply_text('فایل خود را آپلود کنید')
                        user.state = "waiting_upload"
                    if update.message.text == "انصراف":
                        update.message.reply_text('متاسفانه امکان حل این سوال را از دست دادید!')
                        user.current_problem = ""
                        user.state = "game_state"
                    if update.message.text == "بازگشت":
                        user.state = "game_state"
        elif user.state == "waiting_upload":
            if update.message.document:
                try:
                    user.submited.append(user.current_problem)
                    update.message.document.get_file().download(".//responses//" + update.message.document.file_name)#update.message.document.file_name +
                    update.message.reply_text("فایل دریافت شد")
                    update.message.forward(-1001332379255)  # ALA_Responses Channel ID
                    user.current_problem = ""
                    user.state = "game_state"
                except:
                    update.message.reply_text("لطفا پاسخ خود را مجددا بارگزاری نمایید")
            elif update.message.text == "انصراف":
                update.message.reply_text('متاسفانه امکان حل این سوال را از دست دادید!')
                user.current_problem = ""
                user.state = "game_state"
            else:
                update.message.reply_text("لطفا فقط فایل به فرمت pdf ارسال کنید")
        elif user.state == "send_message":
            if update.message.text:
                update.message.reply_text('پیام شما دریافت شد')
                update.message.forward(-1001228175249)  # ALA_Questions Channel ID
                user.state = "game_state"
        elif user.state == "send_suggestions":
            if update.message.text:
                update.message.reply_text('پیشنهاد شما دریافت شد. خیلی ممنون!')
                update.message.text += '#suggestion'
                update.message.forward(-1001203878951)
                # update.message.forward(-1001156816304)
                user.state = "start"
                # show state keyboard!!!!!!
        if user.state == "start":
            reply_keyboard = [['مسابقه عید', 'امکانات دیگر'], ['درباره ما', 'پیشنهادات و انتقادات']]
            update.message.reply_text("یکی از گزینه‌های زیر را انتخاب فرمایید",
                                      reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        elif user.state == "challenge":
            reply_keyboard = [['توضیحات', 'شرکت در مسابقه'], ['بازگشت']]
            update.message.reply_text('یکی از گزینه‌های زیر را انتخاب فرمایید',
                                      reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        elif user.state == "game_state":
            if user.current_problem is "":
                reply_keyboard = [['دریافت سوال جدید', 'وضعیت سوال‌ها'], ['جدول امتیازات'],
                                  ['درخواست کمک از تدریسیاران'], ['بازگشت']]
            else:
                reply_keyboard = [['سوال فعلی', 'وضعیت سوال‌ها'], ['جدول امتیازات'],
                                  ['درخواست کمک از تدریسیاران'],
                                  ['بازگشت']]
            update.message.reply_text('لطفا یکی از گزینه‌های زیر را انتخاب کنید',
                                      reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
            pass
        elif user.state == "thinking":
            reply_keyboard = [['ارسال پاسخ', 'انصراف'], ['بازگشت']]
            update.message.reply_text('لطفا یکی از گزینه‌های زیر را انتخاب کنید',
                                      reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
            pass
        elif user.state == "waiting_upload":
            # update.message.reply_text('فایل خود را آپلود کنید')
            pass

        if chat_id in admins:
            if user.state == "start":
                if update.message.text:
                    if update.message.text == "پاسخ به سوالات":
                        update.message.reply_text(
                            'لطفا ابتدا یک پیام از مخاطب مورد نظر فوروارد کنید')
                        user.state = "choosePartner"
            elif user.state == "choosePartner":
                if update.message:
                    if update.message.text == 'بازگشت':
                        user.state = 'start'
                    elif update.message.forward_from:
                        user.pid = update.message.forward_from.id
                        update.message.reply_text('مخاطب با شناسه' + str(user.pid) + 'انتخاب شد.'
                                                  + '\n' + 'حال پیام مورد نظر خود را وارد کنید')
                        user.state = "responding"

            elif user.state == "responding":
                if update.message:
                    if update.message.text == 'بازگشت':
                        user.state = 'start'
                    else:
                        bot.send_message(chat_id=user.pid, text=update.message.text)
                        update.message.reply_text('پیام مورد نظر ارسال شد')
                        user.pid = 0
                        user.state = 'start'
            # print(uid)
            #     print("i'm here")
            #     if update.message:
            #         bot.send_message(chat_id=uid, text=update.message.text)

            if user.state == "start":
                reply_keyboard = [['مسابقه عید', 'امکانات دیگر'], ['درباره ما', 'پیشنهادات و انتقادات'],
                                  ['پاسخ به سوالات']]
                update.message.reply_text("یکی از گزینه‌های زیر را انتخاب فرمایید",
                                          reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
            elif user.state == 'choosePartner':
                reply_keyboard = [['بازگشت']]
                update.message.reply_text("در صورت پشیمان شدن گزینه بازگشت را انتخاب کنید",
                                          reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
            elif user.state == 'responding':
                reply_keyboard = [['بازگشت']]
                update.message.reply_text("در صورت پشیمان شدن گزینه بازگشت را انتخاب کنید",
                                          reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

        write_json()


def error_callback(bot, update, error):
    try:
        raise error
    except Unauthorized:
        pass
    # remove update.message.chat_id from conversation list
    except BadRequest:
        pass
    # handle malformed requests - read more below!
    except TimedOut:
        update.message.reply_text("لطفا مجددا تلاش فرمایید")
    # handle slow connection problems
    except NetworkError:
        pass
    except ChatMigrated as e:
        pass
    # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        pass
        # handle all other telegram related errors


def write_json():
    with open('data.json', 'w') as fp:
        json.dump(user_dict, fp, default=lambda o: o.__dict__)


def main():
    global admins
    admins = [73675932]
    global user_dict
    global problem_list
    try:
        with open('data.json', 'r') as fp:
            temp_dict = json.load(fp)
            user_dict = {}
            for k, v in temp_dict.items():
                user_dict[k] = User(**v)
    except:
        print("it is execpt in reading data.json")
        user_dict = {}
    try:
        with open('problems.json', 'r') as fp:
            problem_list = json.load(fp)["problems"]
            print(problem_list)
    except:
        print("it is execpt in reading problem")
        problem_list = []
    uid = 0
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(MessageHandler(Filters.all, update_handler))
    dp.add_error_handler(error_callback)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
