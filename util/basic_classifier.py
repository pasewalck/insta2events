import re

from tracker import PostTracker

english_keywords = [
    'event', 'festival', 'concert', 'party', 'celebration',
    'gathering', 'exhibition', 'launch', 'ceremony', 'workshop',
    'strike']
german_keywords = [
    'ereignis', 'festival', 'konzert', 'party', 'feier',
    'zusammenkunft', 'ausstellung', 'einführung', 'zeremonie', 'workshop',
    'konferenz', 'treffen', 'gala', 'eröffnung', 'show', 'aktion', 'streik'
]

english_keywords_negative = [
    'today', 'we did', 'made', 'striked', 'yesterday', 'tomorrow']
german_keywords_negative = [
    'heute', 'haben wir', 'gemacht', 'gestreikt', 'gestern', 'morgen'
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
date_pattern = r'\d{1,2}[.\-\/][ ]?\d{1,2}[.\-\/]'


def classic_classifier(post: PostTracker):
    text = post.caption()
    contains = 0
    for word in (
            english_keywords + german_keywords + english_weekdays + german_weekdays + german_months + english_months):
        if word.lower() in text.lower():
            contains += 1
    for word in (english_keywords_negative + german_keywords_negative):
        if word.lower() in text.lower():
            contains -= 1
    match = re.search(date_pattern, text, re.IGNORECASE)
    if (match is not None and match.group() != "") or contains >= 1:
        return True
    else:
        return False
