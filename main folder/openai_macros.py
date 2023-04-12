# imports ============================================
import pickle
import re
import random
import json
import pandas as pd
# API ============================================
import openai
import nltk
nltk.download('omw-1.4')
# python files ============================================
from becca import users_dictionary, current_user, color_names_df, styles_df
# TODO: api_file.py is ignored by github for privacy reasons
from api_file import API_KEY
# import babble_macros
# ============================================
from typing import Dict, Any, List
from collections import defaultdict
from emora_stdm import Macro, Ngrams, DialogueFlow

# variables ============================================
openai.api_key = API_KEY

# functions ============================================

# asks the API to recommend a clothing item
def recommendClothing(interest, color, style):

    prompt = "Recommend a real clothing item for someone who likes " + interest + " and the color " + color + " and the " + style + ". Put your response in the same form as this example response: Athleta's Speedlight Skort in the color Blue Tropics. Do not say anything more than this example shows."

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        # determines the randomness of the API's response; 0 = response is more focused and deterministic ~ 0.8 = response is more random
        temperature=0,
        messages=[
            {"role": "system", "content": "You are a chatbot"},
            {"role": "user", "content": prompt},
        ]
    )

    result = response['choices'][0]['message']['content'].strip()
    return str(result)


# asks the API to recommend a clothing item based on the feedback from the last recommendation
def recommendClothingAfterFeedback(interest, color, style, lastRec, feedback):

    prompt = "Recommend a real clothing item for someone who likes" + interest + "and the color" + color + "and the" +  style + ". This person gave the following feedback to your last recommendation of " + lastRec + ": " + feedback + "Put your response in the same form as this example response: Athleta's Speedlight Skort in the color Blue Tropics. Do not say anything more than this example shows."

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0,
        messages=[
                {"role": "system", "content": "You are a chatbot"},
                {"role": "user", "content": prompt},
            ]
    )

    result = response['choices'][0]['message']['content'].strip()
    return str(result)


# determines the sentiment of the user's response
def feedbackSentiment(feedback):

    prompt = "You are a bot that determines if feedback is positive, nuetral, or negative. I just recommended a peice of clothing to a user. This is their response: " + feedback + " Is the sentiment of this response positive, negative, or neutral. Give a one word response. Do not put a period at the end of your response. Only say positive, negative, or neutral and say nothing else."

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0,
        messages=[
                {"role": "system", "content": "You are a chatbot"},
                {"role": "user", "content": prompt},
            ]
    )

    result = response['choices'][0]['message']['content'].strip()
    return str(result)


# macros ============================================

# recommends another clothing item -- message output based on if the user's previous feedback was negative
class MacroGPTNegativeFeedbackRecommend(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global users_dictionary
        global current_user
        global styles_df
        global lastRec
        global randInt1
        global randInt2
        global randInt3
        global feedback

        # select the user's dictionary
        user_nested_dictionary = users_dictionary[current_user]

        # save the user's hobbies, styles, and fav colours list
        user_hobbies_list = user_nested_dictionary['hobbies_list']
        user_style_list = user_nested_dictionary['style_list']
        user_colors_list = user_nested_dictionary['fav_colors_list']


        rec = recommendClothingAfterFeedback(
			interest=user_hobbies_list[randInt1],
			color=user_colors_list[randInt2],
			style=user_style_list[randInt3],
			lastRec = lastRec,
			feedback=feedback
		)

        lastRec = rec

        return "I think you might like this recommendation a little better: " + rec + "."


# returns True if the user's feedback was negative, else False
class MacroGetFeedbackSentiment(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global feedback

        feedback = ngrams.text()
        sentiment = feedbackSentiment(feedback)

        if sentiment == "Negative" or sentiment == "negative" or sentiment == "Negative." or sentiment == "negative.":
            return True
        else:
            return False


# recommends another clothing item -- message output based on if the user's previous feedback was positive
class MacroGPTRecommendAfterPositiveFeedback(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global users_dictionary
        global current_user
        global styles_df
        global lastRec
        global randInt1
        global randInt2
        global randInt3

        # select the user's dictionary
        user_nested_dictionary = users_dictionary[current_user]

        # save the user's hobbies, styles, and fav colours list
        user_hobbies_list = user_nested_dictionary['hobbies_list']
        user_style_list = user_nested_dictionary['style_list']
        user_colors_list = user_nested_dictionary['fav_colors_list']

        # randomly select an item from each list
        randInt1 = random.randint(0, len(user_hobbies_list)-1)
        randInt2 = random.randint(0, len(user_colors_list)-1)
        randInt3 = random.randint(0, len(user_style_list)-1)


        rec = recommendClothing(
			interest=user_hobbies_list[randInt1],
			color=user_colors_list[randInt2],
			style=user_style_list[randInt3]
		)

        lastRec = rec
        return "I also think you might like this " + rec + "."


# recommends a clothing item
class MacroGPTRecommend(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global users_dictionary
        global current_user
        global styles_df
        global lastRec
        global randInt1
        global randInt2
        global randInt3


        # select the user's dictinary
        user_nested_dictionary = users_dictionary[current_user]

        # save the user's hobbies, styles, and fav colours list
        user_hobbies_list = user_nested_dictionary['hobbies_list']
        user_style_list = user_nested_dictionary['style_list']
        user_colors_list = user_nested_dictionary['fav_colors_list']

        # randomly select an item from each list
        randInt1 = random.randint(0, len(user_hobbies_list)-1)
        randInt2 = random.randint(0, len(user_colors_list)-1)
        randInt3 = random.randint(0, len(user_style_list)-1)


        rec = recommendClothing(
			interest=user_hobbies_list[randInt1],
			color=user_colors_list[randInt2],
			style=user_style_list[randInt3]
		)

        lastRec = rec

        return "I think you'd really like this " + rec + "."