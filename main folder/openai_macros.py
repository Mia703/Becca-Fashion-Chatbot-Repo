# imports ============================================
import pickle
import re
import random
import json
import pandas as pd
import openai
# python files ============================================
# api_file.py is ignored by github for privacy reasons
import api_file
import becca
import babble_macros
# ============================================
from typing import Dict, Any, List
from collections import defaultdict
from emora_stdm import Macro, Ngrams, DialogueFlow

class MacroGPTNegativeFeedbackRecommend(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
		# TODO: not sure if this works it's either becca.users_dictionary or just users_dictionary
        global users_dictionary
        global current_user
        global styles_df
        global lastRec
        global randInt1
        global randInt2
        global randInt3
        global feedback

        user_nested_dictionary = users_dictionary[current_user]

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


class MacroGetFeedbackSentiment(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global feedback

        feedback = ngrams.text()
        sentiment = feedbackSentiment(feedback)

        if sentiment == "Negative" or sentiment == "negative" or sentiment == "Negative." or sentiment == "negative.":
            return True
        else:
            return False


class MacroGPTRecommendAfterPositiveFeedback(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global users_dictionary
        global current_user
        global styles_df
        global lastRec
        global randInt1
        global randInt2
        global randInt3

        user_nested_dictionary = users_dictionary[current_user]

        user_hobbies_list = user_nested_dictionary['hobbies_list']
        user_style_list = user_nested_dictionary['style_list']
        user_colors_list = user_nested_dictionary['fav_colors_list']

        randInt1 = random.randint(0,len(user_hobbies_list)-1)
        randInt2 = random.randint(0, len(user_colors_list)-1)
        randInt3 = random.randint(0, len(user_style_list)-1)

        rec = recommendClothing(
			interest=user_hobbies_list[randInt1], 
			color=user_colors_list[randInt2], 
			style=user_style_list[randInt3]
		)

        lastRec = rec
        return "I also think you might like this " + rec + "."


class MacroGPTRecommend(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global users_dictionary
        global current_user
        global styles_df
        global lastRec
        global randInt1
        global randInt2
        global randInt3

        user_nested_dictionary = users_dictionary[current_user]

        user_hobbies_list = user_nested_dictionary['hobbies_list']
        user_style_list = user_nested_dictionary['style_list']
        user_colors_list = user_nested_dictionary['fav_colors_list']

        randInt1 = random.randint(0,len(user_hobbies_list)-1)
        randInt2 = random.randint(0, len(user_colors_list)-1)
        randInt3 = random.randint(0, len(user_style_list)-1)

        rec = recommendClothing(
			interest=user_hobbies_list[randInt1], 
			color=user_colors_list[randInt2], 
			style=user_style_list[randInt3]
		)

        lastRec = rec
        return "I think you'd really like this " + rec + "."


def recommendClothing(interest, color, style):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messs=[
                {"role": "system", "content": "You are a chatbot"},
                {"role": "user", "content": "Recommend a real clothing item for someone who likes" + interest + "and the color" + color + "and the" + style + ". Put your response in the same form as this example response: Athleta's Speedlight Skort in the color Blue Tropics. Do not say anything more than this example shows."},
            ]
    )

    result = ''
    for choice in response.choices:
        result += choice.message.content

    return result


def recommendClothingAfterFeedback(interest, color, style, lastRec, feedback):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "You are a chatbot"},
                {"role": "user", "content": "Recommend a real clothing item for someone who likes" + interest + "and the color" + color + "and the" +  style + ". This person gave the following feedback to your last recommendation of " + lastRec + ": " + feedback + "Put your response in the same form as this example response: Athleta's Speedlight Skort in the color Blue Tropics. Do not say anything more than this example shows."},
            ]
    )

    result = ''
    for choice in response.choices:
        result += choice.message.content

    return result




def feedbackSentiment(feedback):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "You are a chatbot"},
                {"role": "user", "content": "You are a bot that determines if feedback is positive, nuetral, or negative. I just recommended a peice of clothing to a user. This is their response:" + feedback + "Is the sentiment of this response positive, negative, or neutral. Give a one word response. Do not put a period at the end of your response. Only say positive, negative, or neutral and say nothing else."},
            ]
    )

    result = ''
    for choice in response.choices:
        result += choice.message.content

    print(result)
    return result
