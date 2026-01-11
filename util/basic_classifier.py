import re

from util.config import CLASSIFIER_USE_OCR

english_keywords = [
    'event', 'festival', 'concert', 'party', 'celebration',
    'gathering', 'exhibition', 'launch', 'ceremony', 'workshop',
    'conference', 'meetup', 'gala', 'opening', 'show'
]
german_keywords = [
    'ereignis', 'festival', 'konzert', 'party', 'feier',
    'zusammenkunft', 'ausstellung', 'einführung', 'zeremonie', 'workshop',
    'konferenz', 'treffen', 'gala', 'eröffnung', 'show', 'aktion'
]
english_weekdays = [
    'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
]
german_weekdays = [
    'montag', 'dienstag', 'mittwoch', 'donnerstag', 'freitag', 'samstag', 'sonntag'
]
english_months = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
                  "november", "december"]
german_months = ["januar", "februar", "märz", "april", "mai", "juni", "juli", "august", "september", "oktober",
                 "november", "dezember"]
date_pattern = r'/\d{1,2}[.\-\/][ ]?\d{1,2}[.\-\/]/'


def classic_classifier(post):
    text = post.caption()
    if CLASSIFIER_USE_OCR:
        text += post.ocr_output()
    contains = False
    for word in (
            english_keywords + german_keywords + english_weekdays + german_weekdays + german_months + english_months):
        if word.lower() in text.lower():
            contains = True
    match = re.search(date_pattern, text, re.IGNORECASE)
    if (match is not None and match.group() != "") or contains:
        return True
    else:
        return False
