import json
import re
import csv
from requests import get
from bs4 import BeautifulSoup as BS

class SentenceExample(object):    
    def remove_html_tag(self, text):
        cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
        return re.sub(cleanr, '', text)
    
    def get_goal_id(self):
        url = "https://iknow.jp/content/japanese"
        response = get(url)

        html_soup = BS(response.text, 'html.parser')

        items = html_soup.find_all('div', class_='details shiv-border-box-sizing')
        
        course_ids = []
        for item in items:
            a_item = item.find('a', href=True)
            href = a_item.get('href')
            splited = href.split('/')
            course_id = splited[-1]

            course_ids.append(course_id)

        for course_id in course_ids:
            self.write_to_csv(course_id)
    
    def write_to_csv(self, course_id):
        writer = csv.writer(open("../files/scrap.csv", 'a'))

        url = "https://iknow.jp/api/v2/goals/"+course_id
        response = get(url)
        json_data = json.loads(response.text)

        goal_items = json_data.get('goal_items')

        # header
        row = ['w', 'w_part_of_speech', 'w_romaji', 'w_meaning', 's_kanji', 's_hiragana', 's_romaji', 's_meaning']
        writer.writerow(row)

        for goal_item in goal_items:
            item = goal_item.get('item')

            # get word info
            word = item.get('cue', {})
            word_data = word.get('text')
            word_part_of_speech = word.get('part_of_speech')
            word_romaji = word.get('transliterations', {}).get('Latn')

            word_translation = item.get('response', {}).get('text')

            sentences = goal_item.get('sentences')
            for sentence in sentences:
                row = []

                cued_data = sentence.get('cue', {})
                translation = sentence.get('response', {}).get('text')

                hira = self.remove_html_tag(cued_data.get('transliterations', {}).get('Hira'))
                jpn = self.remove_html_tag(cued_data.get('transliterations', {}).get('Jpan'))
                latin = self.remove_html_tag(cued_data.get('transliterations', {}).get('Latn'))

                #word info
                row.append(word_data)
                row.append(word_romaji)
                row.append(word_part_of_speech)
                row.append(word_translation)

                # sentence section
                row.append(jpn)
                row.append(hira)
                row.append(latin)
                row.append(translation)
            
                writer.writerow(row)

if __name__ == "__main__":
    se = SentenceExample()
    se.get_goal_id()