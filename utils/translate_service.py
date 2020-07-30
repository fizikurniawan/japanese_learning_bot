import gtts
from googletrans import Translator

class TranslateService(object):
    def __init__(self, *args, **kwargs):
        self.src = kwargs.get('src', 'id')
        self.dest = kwargs.get('dest', 'ja')
        self.voice_desc = kwargs.get('voice_desc', self.dest)

        self.translator = Translator()
    
    def translate(self, text, create_voice=False,):
        translator = self.translator
        translated = translator.translate(text, src=self.src, dest=self.dest)

        # create voice
        if create_voice:
            self.create_voice(translated.text, lang=self.voice_desc)
        
        trans_obj = {
            "text": translated.text,
            "pronunciation": translated.pronunciation,
            "extra_data": translated.extra_data
        }

        return trans_obj
    
    def create_voice(self, text, *args, **kwargs):
        lang = kwargs.get('lang', 'ja')

        tts = gtts.gTTS(text, lang=lang)
        tts.save("files/result.mp3")