import romkan
from pykakasi import kakasi

class KanaConverter(object):
    def __init__(self):
        kks = kakasi()
        kks.setMode('J', 'H')

        self.conv = kks.getConverter()

    def kanji_to_romaji(self, text):
        convert = self.conv

        hiragana_text = convert.do(text)
        romaji_text = romkan.to_roma(hiragana_text)
        
        return (hiragana_text, romaji_text)