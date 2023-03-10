import yaml
import os

def load_emojis():
    # Load the list of emojis from yaml file
    with open(os.path.join(os.path.dirname(__file__), 'data.yaml'), 'r') as f:
        emojis = yaml.safe_load(f)['emojis']
    return emojis

# get the emoji for the weather
def get_emoji(forecast, isDayTime):
    forecast = forecast.lower()
    emoji_dict = load_emojis()
    if not isDayTime:
        # if it is night time, return the night time emoji
        return 'night', emoji_dict['night']['text']
    # check the keywords for each emoji to see if there is a match in the forecast
    # for each emoji that matches, add it to a dictionary and list the number of matches
    emoji_matches = {}
    for emoji in emoji_dict:
        emoji_matches[emoji] = 0
        for keyword in emoji_dict[emoji]['keywords']:
            if keyword in forecast:
                emoji_matches[emoji] += 1
    # return the emoji's key and text with the most matches
    emoji_key = max(emoji_matches, key=emoji_matches.get)
    emoji_text = emoji_dict[max(emoji_matches, key=emoji_matches.get)]['text']
    return emoji_key, emoji_text