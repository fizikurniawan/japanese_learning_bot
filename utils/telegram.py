import romkan
import pandas as pd
import threading
from telegram.ext import Updater, CommandHandler

from .constants import BOT_TOKEN, USER_ID, INTERVAL_SENDING
from .translate_service import TranslateService as TS
from .kana_converter import KanaConverter as KC


class TelegramService(object):

    def __init__(self):
        self.send_every_x()

    # sending message every INTERVAL_SENDING minutes
    def send_every_x(self):
        threading.Timer(INTERVAL_SENDING, self.send_every_x).start()
        print("Sending sentence....")

        self.send_sentence_every_x()

    def get_command_and_args(self, message):
        chat_id = message.chat_id
        text = message.text
        args = []
        command = "word"
        content = []

        splitted = text.split(" ")

        for word in splitted:
            if "/" in word:
                command = word.replace("/", "")
            elif "*" in word:
                args.append(word.replace("*", ""))
            else:
                content.append(word)

        content = " ".join(content)

        return (chat_id, command, args, content)

    def listen_action(self):
        updater = Updater(BOT_TOKEN, use_context=True)
        updater.dispatcher.add_handler(CommandHandler("tr", self.translate_word))
        updater.dispatcher.add_handler(CommandHandler("rd", self.send_random_word))
        updater.dispatcher.add_handler(
            CommandHandler("sentence", self.send_random_sentence)
        )
        updater.dispatcher.add_handler(CommandHandler("vocab", self.send_specify_level))

        # Run the bot
        updater.start_polling()
        updater.idle()

    def translate_word(self, update, context):
        try:
            chat_id, command, args, content = self.get_command_and_args(update.message)

            # get src and dest language
            args = dict(enumerate(args))
            from_lang = args.get(0, "id")
            to_lang = args.get(1, "ja")

            ts = TS(src=from_lang, dest=to_lang)
            translation = ts.translate(content, create_voice=True)

            trans_text = translation.get("text", content)
            trans_pronunciation = translation.get("pronunciation", content)

            text_to_send = "Translated: %s\nPronunciation: %s " % (
                trans_text,
                trans_pronunciation,
            )

            context.bot.send_message(chat_id=chat_id, text=text_to_send)
            context.bot.send_voice(
                chat_id=chat_id, voice=open("files/result.mp3", "rb")
            )
        except Exception as error:
            print(error)

    def send_random_word(self, update, context):
        try:
            dictionary = pd.read_csv("files/dictionary.csv")

            kana = dictionary["Vocab-kana"].sample(1).values[0]
            ts = TS(src="ja", dest="id", voice_desc="ja")
            translation = ts.translate(kana)
            ts.create_voice(kana)

            trans_text = translation.get("text", kana)
            trans_pronunciation = romkan.to_roma(kana)

            chat_id = update.message.chat_id
            text_to_send = "From: %s \nPronunciation: %s \nMeaning (ID): %s" % (
                kana,
                trans_pronunciation,
                trans_text,
            )

            context.bot.send_message(chat_id=chat_id, text=text_to_send)
            context.bot.send_voice(
                chat_id=chat_id, voice=open("files/result.mp3", "rb")
            )
        except Exception as error:
            print(error)

    def send_specify_level(self, update, context):
        try:
            level = context.args[0]
            file_name = {
                'n5': "files/N5_dicts.csv",
                'n4': "files/N4_dicts.csv",
                'n3': "files/N3_dicts.csv",
                'n2': "files/N2_dicts.csv",
                'n1': "files/N1_dicts.csv",
            }

            file_path = file_name.get(level, "files/N5_dicts.csv")

            dictionary = pd.read_csv(file_path)

            list_data = dictionary[["kanji", "kana", "primary", "meanings"]].sample(1).values[0]

            kanji = list_data[0]
            kana = list_data[1]
            meanings = list_data[2] + ", " + list_data[3]

            kc = KC()
            _, romaji = kc.kanji_to_romaji(kana)

            # create sound
            ts = TS()
            ts.create_voice(kana, lang="ja")

            chat_id = update.message.chat_id
            text_to_send = "Kanji: %s \nHira: %s \nRomaji: %s \nMeaning (EN): %s" % (
                kanji,
                kana,
                romaji,
                meanings,
            )

            context.bot.send_message(chat_id=chat_id, text=text_to_send)
            context.bot.send_voice(
                chat_id=chat_id, voice=open("files/result.mp3", "rb")
            )
        except Exception as error:
            print(error)

    def send_random_sentence(self, update, context):
        try:
            dictionary = pd.read_csv("files/sentences.csv")
            selected_data = dictionary[["kana", "meaning"]].sample(1).values[0]

            kana = selected_data[0]
            meaning = selected_data[1]

            # let's convert to romaji
            kc = KC()
            katakana, romaji = kc.kanji_to_romaji(kana)

            chat_id = update.message.chat_id
            text_to_send = "From:\n%s \n%s \n%s \n\nMeaning (ID): \n%s" % (
                kana,
                katakana,
                romaji,
                meaning,
            )

            # create voice
            ts = TS()
            ts.create_voice(kana, lang="ja")

            context.bot.send_message(chat_id=chat_id, text=text_to_send)
            context.bot.send_voice(
                chat_id=chat_id, voice=open("files/result.mp3", "rb")
            )
        except Exception as error:
            print(error)

    def send_sentence_every_x(self):
        updater = Updater(BOT_TOKEN, use_context=True)

        seleted_column = ['w','w_part_of_speech','w_romaji','w_meaning','s_kanji','s_hiragana','s_romaji','s_meaning']

        dictionary = pd.read_csv("files/scheduler_dicts.csv")
        selected_data = dictionary[seleted_column].sample(1).values[0]

        # create translate to ID and voice
        ts = TS(src='en', dest='id')
        translation_1 = ts.translate(selected_data[3], create_voice=False)
        word_in_id = translation_1.get("text", '-')

        translation_2 = ts.translate(selected_data[7], create_voice=False)
        sentence_in_id = translation_2.get("text", '-')

        # send word information
        word_info_message = "🇯🇵: %s \n🅰: %s \n🔑: %s \n🇬🇧: %s\n🇮🇩: %s" % (
            selected_data[0],
            selected_data[1],
            selected_data[2],
            selected_data[3],
            word_in_id
        )
        sentence_message = "🇯🇵: %s \n\n🇯🇵: %s \n\n🅰: %s \n\n🇬🇧: %s\n\n🇮🇩: %s" % (
            selected_data[4],
            selected_data[5],
            selected_data[6],
            selected_data[7],
            sentence_in_id
        )
        
        # send word section
        ts.create_voice(selected_data[0], lang='ja')
        updater.bot.send_message(USER_ID, text=word_info_message)
        updater.bot.send_voice(
            USER_ID, voice=open("files/result.mp3", "rb")
        )

        # send sentence section
        ts.create_voice(selected_data[4], lang='ja')
        updater.bot.send_message(USER_ID, text=sentence_message)
        updater.bot.send_voice(
            USER_ID, voice=open("files/result.mp3", "rb")
        )