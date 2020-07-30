import romkan
import pandas as pd
from telegram.ext import Updater, CommandHandler

from .constants import BOT_TOKEN
from .translate_service import TranslateService as TS


class TelegramService(object):

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

            text_to_send = "Translated: %s\nPronunciation: %s "% (
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
            dictionary = pd.read_csv('files/dictionary.csv')

            kana = dictionary['Vocab-kana'].sample(1).values[0]
            ts = TS(src='ja', dest='id', voice_desc='ja')
            translation = ts.translate(kana)
            ts.create_voice(kana)

            trans_text = translation.get("text", kana)
            trans_pronunciation = romkan.to_roma(kana)

            chat_id = update.message.chat_id
            text_to_send = "From: %s \nPronunciation: %s \nMeaning (ID): %s" % (
                kana,
                trans_pronunciation,
                trans_text
            )

            context.bot.send_message(chat_id=chat_id, text=text_to_send)
            context.bot.send_voice(
                chat_id=chat_id, voice=open("files/result.mp3", "rb")
            )
        except Exception as error:
            print(error)