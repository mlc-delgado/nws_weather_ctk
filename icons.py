import yaml
import os

# load the emoji dictionary
def load_emoji():
    with open(os.path.join(os.path.dirname(__file__), 'emojis.yaml'), 'r') as f:
        emoji_dict = yaml.safe_load(f)
    f.close()
    return emoji_dict

# get the emoji for the weather
def get_emoji(forecast, isDayTime):
    forecast = forecast.lower()
    emoji_dict = load_emoji()
    if not isDayTime:
        # if it is night time, return the night time emoji
        return emoji_dict['night']['text']
    # check the keywords for each emoji to see if there is a match in the forecast
    # for each emoji that matches, add it to a dictionary and list the number of matches
    emoji_matches = {}
    for emoji in emoji_dict:
        emoji_matches[emoji] = 0
        for keyword in emoji_dict[emoji]['keywords']:
            if keyword in forecast:
                emoji_matches[emoji] += 1
    # return the text of the emoji with the most matches
    return emoji_dict[max(emoji_matches, key=emoji_matches.get)]['text']