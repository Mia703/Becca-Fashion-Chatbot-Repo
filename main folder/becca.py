# imports ============================================
import pickle
import re
import random
import json
import string
import pandas as pd
# API ============================================
import openai
import nltk
# nltk.download('omw-1.4')
# ============================================
from typing import Dict, Any, List
from collections import defaultdict
from emora_stdm import Macro, Ngrams, DialogueFlow

# variables ============================================
users_dictionary = {}
current_user = ""

# import colour names csv file
color_names_df = pd.read_csv('./resources/color_names.csv')

# import styles csv file
styles_df = pd.read_csv('./resources/styles.csv')

# imports api key for openai
#openai.api_key_path = './resources/openai_api.txt'
openai.api_key = ''


# saves the user's feedback from recommendation
user_feedback = ''

# saves the last recommendation to the user 
last_recommendation = ''


# macros ============================================

# saves and returns the user's name
# TODO: done
class MacroGetName(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global users_dictionary
        global current_user

		firstname = None

		# get the user's response
		user_response = ngrams.text()

        prompt = 'I asked a person to tell me their name. This was their response: \"' + user_response + '\". Respond with only their name. Do not put any periods or say anything else, only respond with their name.'
        
		response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            temperature=0,
            max_tokens=200,
            messages=[
                {'role': 'system', 'content': 'You are a chatbot'},
                {'role': 'user', 'content': prompt},
            ]
        )

		# get the result from the api
        result = response['choices'][0]['message']['content'].strip()

        # save the name without any punctuation
		firstname = result.strip(string.punctuation)

		# save the current user -- in lowercase for name ID
		current_user = firstname.lower()


        vars['FIRSTNAME'] = firstname.capitalize()

        vars['RETURN_USER'] = createUserCheck()

        return True


# saves the user's age
class MacroSaveAge(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global users_dictionary
        global current_user

        r = re.compile(r"([0-9]+)")
        m = r.search(ngrams.text())

        # if there is no match, return false
        if m is None:
            return False

        # else, there is a match
        # set the var 'age' to None
        age = None

        # if m isn't empty -- true
        if m.group():
            # assign 'age' to the match
            age = m.group()

        # save the user's age as an int
        users_dictionary[current_user]['age'] = int(age)

        # save the user's age in a var for dialogue
        vars['USER_AGE'] = age

        return True


# returns a response to the user's age
class MacroReturnAgeResponse(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global users_dictionary
        global current_user

        user_age = users_dictionary[current_user]['age']

        if user_age < 18:
            return str('You\'re so young! You sure you should be using my services? \U0001F928\n')

        if user_age >= 18 and user_age <= 25:
            return str('Oh, okay! You\'re a young adult. I can definitely help you!\n')

        elif user_age >= 26 and user_age <= 30:
            return str('So, your an adult adult. I can still help you though!\n')

        else:
            return str('Omg, you\'re so old! Ah, I mean, you\'re so mature...\n I can still help you though.\n')


# save the user's occupation
class MacroSaveOccupation(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global users_dictionary
        global current_user

        # print(vars['USER_OCCUPATION'])
        user_occupation = vars['USER_OCCUPATION']

        # save the user's occupation
        users_dictionary[current_user]['occupation'] = str(user_occupation).lower()
        # print(users_dictionary)

        # return a random response to the user's occupation
        responses = ['Oh, cool! You\'re a ',
                     'That\'s interesting! You work as a ',
                     'I\'ve always been fascinated by being a ',
                     'I bet you see and do a lot of interesting things as a ',
                     'That sound like a really important job, as a ']

        return str(random.choice(responses) + user_occupation + '.')


# randomly responds to the user's occupation
class MacroOccupationResponse(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        # randomly return a response to push the conversation forward
        responses = ['What is your favorite part of your job?',
                     'What do you do at work on a daily basis?',
                     'What\'s the best thing about your job?',
                     'Can you tell me more about what you do?',
                     'How did you get into that field?']

        # tell me more...
        return str('Oh, okay! For me, I love my job!\n '
                   'As a fashion bot, I\'m always looking for new ways to communicate better and connect with my users,\n '
                   'especially since I was born like a month ago. \U0001F609 ' + random.choice(responses))


# saves the user's hobbies
class MacroSaveHobby(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global users_dictionary
        global current_user

        # get the user's hobby
        user_hobby = str(vars['USER_HOBBY'])

        # access the user's dictionary
        user_nested_dictionary = users_dictionary[current_user]

        # access the user's hobby list
        user_nested_list = user_nested_dictionary['hobbies_list']

        # append the hobby to the list
        if (user_hobby not in user_nested_list):
            user_nested_list.append(user_hobby)

# print(users_dictionary)


# save the user's favourite colours
class MacroSaveFavoriteColor(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global users_dictionary
        global current_user
        global color_names_df

        # get the user's colour
        user_color_name = str(vars['USER_COLOR'])

        # search the dataframe for colour name
        # -- returns a dataframe with the row of the colour
        df_results = color_names_df.loc[color_names_df['Name'] == user_color_name]
        # print(df_results)

        # get the index of the row
        color_index = list(df_results.index.values)[0]
        # print(color_index)

        # save the HEX code
        color_hex = df_results['Hex'][color_index]
        # print(color_hex)

        # access the user's dictionary
        user_nested_dictionary = users_dictionary[current_user]

        # access the user's favourite colour list
        user_nested_list = user_nested_dictionary['fav_colors_list']

        # append the HEX code to the list
        if (color_hex not in user_nested_list):
            user_nested_list.append(color_hex)

# print(users_dictionary)


# save the user's not favourite colours
class MacroSaveNotFavoriteColor(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global users_dictionary
        global current_user
        global color_names_df

        # get the user's not favourite colour
        user_colour_name = str(vars['USER_NOT_COLOR'])

        # search the dataframe for colour name
        # -- returns a dataframe with the row of the colour
        df_results = color_names_df.loc[color_names_df['Name'] == user_colour_name]

        # get the index of the row
        color_index = list(df_results.index.values)[0]

        # save the HEX code
        color_hex = df_results['Hex'][color_index]

        # access the user's dictionary
        user_nested_dictionary = users_dictionary[current_user]

        # access the user's not favourite colour list
        user_nested_list = user_nested_dictionary['not_fav_colors_list']

        # append the HEX code to the list
        if (color_hex not in user_nested_list):
            user_nested_list.append(color_hex)

# print(users_dictionary)


# save the user's favourite styles
class MacroSaveStyle(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global users_dictionary
        global current_user
        global styles_df

        # get the user's style or the clothing item associated with the style
        user_style_item = str(vars['USER_STYLE'])
        style = getStyleName(ngrams.text())
        vars['USER_STYLE'] = str(style.lower())
        # access the user's dictionary
        user_nested_dictionary = users_dictionary[current_user]

        # access the user's style list
        user_nested_list = user_nested_dictionary['style_list']

        # append the style name to the list
        if (style not in user_nested_list):
            user_nested_list.append(style)

        return True
        #print(user_nested_dictionary[current_user])

# print(users_dictionary)


# saves the user's favourite clothing items
class MacroSaveFavoriteClothing(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global users_dictionary
        global current_user

        # get the user's clothing item
        user_fav_item = str(vars['USER_FAV_CLOTHING_ITEM'])

        # access the user's dictionary
        user_nested_dictionary = users_dictionary[current_user]

        # access the user's favourite cltohes list
        user_nested_list = user_nested_dictionary['fav_clothes_list']

        # append the clothing item to the list
        if (user_fav_item not in user_nested_list):
            user_nested_list.append(user_fav_item)

# print(users_dictionary)


# saves the user's not favourite clothing items
class MacroSaveNotFavoriteClothing(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global users_dictionary
        global current_user

        # get the user's clothing item from the 'clothing_items_ontology.json'
        user_not_fav_item = str(vars['USER_NOT_FAV_CLOTHING_ITEM'])

        # access the user's dictionary
        user_nested_dictionary = users_dictionary[current_user]

        # access the user's not favorite clothes list
        user_nested_list = user_nested_dictionary['not_fav_clothes_list']

        # append the clothing item name to the list
        if (user_not_fav_item not in user_nested_list):
            user_nested_list.append(user_not_fav_item)

# print(users_dictionary)


# saves the user's current outfit
class MacroSaveOutfit(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global users_dictionary
        global current_user
        global styles_df

        # get the user’s current clothing item
        user_item = str(vars['USER_CURR_ITEM'])
        # print('user item: ' + user_item)

        # if the user is wearing nothing or something similar to nothing, just exit
        if user_item == '':
            return

        # search the dataframe (i.e.: csv file) for the clothing item
        # — returns a dataframe with the row of the clothing item
        df_results = styles_df.loc[styles_df['Clothing'] == user_item]

        # get the index of the row
        curr_item_index = list(df_results.index.values)[0]

        # get the clothing item
        clothing_item = df_results['Clothing'][curr_item_index]

        # get the item’s category
        clothing_category = df_results['Category'][curr_item_index]

        # get the item’s style
        clothing_style = df_results['Style'][curr_item_index]

        # print(str(curr_item_index) + " " + str(clothing_item) + " " + str(clothing_category) + " " + str(clothing_style))

        # access the user’s dictionary
        user_nested_dictionary = users_dictionary[current_user]

        # access the user’s current outfit dictionary
        user_nested_current_outfit_dictionary = user_nested_dictionary['current_outfit_dict']

        # if the clothing item is already in the dictionary, just exit
        for item in user_nested_current_outfit_dictionary:
            # for each clothing_item  (=item) in user_nested_current_outfit_dictionary
            nested_item = user_nested_current_outfit_dictionary[item].get('clothing_item')
            # if the item is already in the dictionary
            if nested_item == user_item:
                # just exit
                return

        # else, add the item to the dicionary
        # get the size of the current outfit dictionary
        dict_index = len(user_nested_current_outfit_dictionary)

        # add +1 to index, to start at 1
        dict_index += 1
        # print('current outfit dictionary size: ' + str(dict_index))

        # add the clothing item, category, and style to the user's current outfit dictinoary
        user_nested_current_outfit_dictionary[dict_index] = dict(
            clothing_item=str(clothing_item),
            clothing_category=str(clothing_category),
            clothing_style=str(clothing_style)
        )

# print(user_nested_current_outfit_dictionary)


# returns whether or not the user has watched the movie
class MacroReturnWatchStatus(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        # get the user's response
        user_response = ngrams.text()

        # pass the response to gpt
        vars['USER_WATCH_STATUS'] = determineWatchStatus(response=user_response)
        return True


# recommendation macros ============================================

# recommends an outfit to the user
class MacroRecommendOutfit(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global users_dictionary
        global current_user
        global styles_df
        global last_recommendation

        # select the user's dictionary
        user_nested_dictionary = users_dictionary[current_user]

        # access the user's lists
        user_hobbies_list = user_nested_dictionary['hobbies_list']
        user_fav_colors_list = user_nested_dictionary['fav_colors_list']
        user_not_fav_colors_list = user_nested_dictionary['not_fav_colors_list']
        user_style_list = user_nested_dictionary['style_list']
        user_fav_clothes_list = user_nested_dictionary['fav_clothes_list']
        user_not_fav_clothes_list = user_nested_dictionary['not_fav_clothes_list']

        # should there be a check here to make sure the list isn't empty
        # an empty list causes an error
        # randomly select an item from each list
        random_hobby_index = random.randint(0, len(user_hobbies_list) - 1)
        random_fav_color_index = random.randint(0, len(user_fav_colors_list) - 1)
        random_not_fav_color_index = random.randint(0, len(user_not_fav_colors_list) - 1)
        random_style_index = random.randint(0, len(user_style_list) - 1)
        random_fav_clothes_index = random.randint(0, len(user_fav_clothes_list) - 1)
        random_not_fav_clothes_index = random.randint(0, len(user_not_fav_clothes_list) - 1)

        # call function
        outfit_recommendation = recommendOutfit(
            hobby=user_hobbies_list[random_hobby_index],
            fav_color=user_fav_colors_list[random_fav_color_index],
            not_fav_color=user_not_fav_colors_list[random_not_fav_color_index],
            user_style=user_style_list[random_style_index],
            fav_item=user_fav_clothes_list[random_fav_clothes_index],
            not_fav_item=user_not_fav_clothes_list[random_not_fav_clothes_index]
        )

        last_recommendation = outfit_recommendation

        return 'To build an outfit, I would recommend ' + outfit_recommendation.lower()


# gets, saves, and returns the user's sentiments about their recommendation
class MacroReturnFeedbackSentiment(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global user_feedback

        # save the user's feedback
        user_feedback = ngrams.text()

        # determine if the user's feedback is positive, neutral, or negative
        user_sentiment = returnUserFeedbackSentiment(feedback=user_feedback)

        # pass the sentiment to the variable
        vars['USER_SENTIMENT'] = str(user_sentiment)
        return True


# recommends an outfit to the user after their positive, neutral, or negative (= sentiment) & feedback
class MacroRecommendOutfitAfterFeedback(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global users_dictionary
        global current_user
        global styles_df
        global last_recommendation
        global user_feedback

        # select the user's dictionary
        user_nested_dictionary = users_dictionary[current_user]

        # access the user's lists
        user_hobbies_list = user_nested_dictionary['hobbies_list']
        user_fav_colors_list = user_nested_dictionary['fav_colors_list']
        user_not_fav_colors_list = user_nested_dictionary['not_fav_colors_list']
        user_style_list = user_nested_dictionary['style_list']
        user_fav_clothes_list = user_nested_dictionary['fav_clothes_list']
        user_not_fav_clothes_list = user_nested_dictionary['not_fav_clothes_list']

        # should there be a check here to make sure the list isn't empty
        # an empty list causes an error
        # randomly select an item from each list
        random_hobby_index = random.randint(0, len(user_hobbies_list) - 1)
        random_fav_color_index = random.randint(0, len(user_fav_colors_list) - 1)
        random_not_fav_color_index = random.randint(0, len(user_not_fav_colors_list) - 1)
        random_style_index = random.randint(0, len(user_style_list) - 1)
        random_fav_clothes_index = random.randint(0, len(user_fav_clothes_list) - 1)
        random_not_fav_clothes_index = random.randint(0, len(user_not_fav_clothes_list) - 1)

        # call function
        outfit_recommendation = recommendOutfitAfterFeedback(
            hobby=user_hobbies_list[random_hobby_index],
            fav_color=user_fav_colors_list[random_fav_color_index],
            not_fav_color=user_not_fav_colors_list[random_not_fav_color_index],
            user_style=user_style_list[random_style_index],
            fav_item=user_fav_clothes_list[random_fav_clothes_index],
            not_fav_item=user_not_fav_clothes_list[random_not_fav_clothes_index],
            feedback=user_feedback,
            sentiment=vars['USER_SENTIMENT']
        )

        last_recommendation = outfit_recommendation

        return 'I think you might like this recommendation a little bit better, I would recommend ' + outfit_recommendation.lower()


# recommends a piece of clothing to match an outfit
class MacroRecommentClothingItem(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global users_dictionary
        global current_user
        global styles_df
        global last_recommendation

        # select the user's dictionary
        user_nested_dictionary = users_dictionary[current_user]

        # access the user's current outfit dictionary
        user_nested_current_outfit_dictionary = user_nested_dictionary['current_outfit_dict']

        clothing_item_sentence = ''
        # iterate through the user's current outfit dictionary
        for item in user_nested_current_outfit_dictionary:
            clothing_item = user_nested_current_outfit_dictionary[item].get('clothing_item')
            clothing_item_style = user_nested_current_outfit_dictionary[item].get('clothing_style')

            # if not the last item in the list, append with comma
            if item == len(user_nested_current_outfit_dictionary):
                clothing_item_sentence += str(clothing_item_style) + ' ' + str(clothing_item)
            else:
                clothing_item_sentence += str(clothing_item_style) + ' ' + str(clothing_item) + ', '

        # access the user's lists
        user_hobbies_list = user_nested_dictionary['hobbies_list']
        user_fav_colors_list = user_nested_dictionary['fav_colors_list']
        user_not_fav_colors_list = user_nested_dictionary['not_fav_colors_list']
        user_style_list = user_nested_dictionary['style_list']
        user_fav_clothes_list = user_nested_dictionary['fav_clothes_list']
        user_not_fav_clothes_list = user_nested_dictionary['not_fav_clothes_list']

        # should there be a check here to make sure the list isn't empty
        # an empty list causes an error
        # randomly select an item from each list
        random_hobby_index = random.randint(0, len(user_hobbies_list) - 1)
        random_fav_color_index = random.randint(0, len(user_fav_colors_list) - 1)
        random_not_fav_color_index = random.randint(0, len(user_not_fav_colors_list) - 1)
        random_style_index = random.randint(0, len(user_style_list) - 1)
        random_fav_clothes_index = random.randint(0, len(user_fav_clothes_list) - 1)
        random_not_fav_clothes_index = random.randint(0, len(user_not_fav_clothes_list) - 1)

        # call function
        outfit_recommendation = recommendClothingItem(
            hobby=user_hobbies_list[random_hobby_index],
            fav_color=user_fav_colors_list[random_fav_color_index],
            not_fav_color=user_not_fav_colors_list[random_not_fav_color_index],
            user_style=user_style_list[random_style_index],
            fav_item=user_fav_clothes_list[random_fav_clothes_index],
            not_fav_item=user_not_fav_clothes_list[random_not_fav_clothes_index],
            outfit=clothing_item_sentence,
        )

        last_recommendation = outfit_recommendation

        # remove the period? -- doesn't matter
        # outfit_recommendation_no_period = outfit_recommendation.replace('.', '')

        return 'I would recommend ' + outfit_recommendation.lower()


# recommends a clothing item after the user's postive, neutral, or negative feedback
class MacroRecommendClothingItemAfterFeedback(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global users_dictionary
        global current_user
        global styles_df
        global last_recommendation
        global user_feedback

        # select the user's dictionary
        user_nested_dictionary = users_dictionary[current_user]

        # access the user's current outfit dictionary
        user_nested_current_outfit_dictionary = user_nested_dictionary['current_outfit_dict']

        clothing_item_sentence = ''
        # iterate through the user's current outfit dictionary
        for item in user_nested_current_outfit_dictionary:
            clothing_item = user_nested_current_outfit_dictionary[item].get('clothing_item')
            clothing_item_style = user_nested_current_outfit_dictionary[item].get('clothing_style')

            # if not the last item in the list, append with comma
            if item == len(user_nested_current_outfit_dictionary):
                clothing_item_sentence += str(clothing_item_style) + ' ' + str(clothing_item)
            else:
                clothing_item_sentence += str(clothing_item_style) + ' ' + str(clothing_item) + ', '

        # access the user's lists
        user_hobbies_list = user_nested_dictionary['hobbies_list']
        user_fav_colors_list = user_nested_dictionary['fav_colors_list']
        user_not_fav_colors_list = user_nested_dictionary['not_fav_colors_list']
        user_style_list = user_nested_dictionary['style_list']
        user_fav_clothes_list = user_nested_dictionary['fav_clothes_list']
        user_not_fav_clothes_list = user_nested_dictionary['not_fav_clothes_list']

        # should there be a check here to make sure the list isn't empty
        # an empty list causes an error
        # randomly select an item from each list
        random_hobby_index = random.randint(0, len(user_hobbies_list) - 1)
        random_fav_color_index = random.randint(0, len(user_fav_colors_list) - 1)
        random_not_fav_color_index = random.randint(0, len(user_not_fav_colors_list) - 1)
        random_style_index = random.randint(0, len(user_style_list) - 1)
        random_fav_clothes_index = random.randint(0, len(user_fav_clothes_list) - 1)
        random_not_fav_clothes_index = random.randint(0, len(user_not_fav_clothes_list) - 1)

        # call function
        outfit_recommendation = recommendClothingItemAfterFeedback(
            hobby=user_hobbies_list[random_hobby_index],
            fav_color=user_fav_colors_list[random_fav_color_index],
            not_fav_color=user_not_fav_colors_list[random_not_fav_color_index],
            user_style=user_style_list[random_style_index],
            fav_item=user_fav_clothes_list[random_fav_clothes_index],
            not_fav_item=user_not_fav_clothes_list[random_not_fav_clothes_index],
            outfit=clothing_item_sentence,
            feedback=user_feedback,
            sentiment=vars['USER_SENTIMENT'],
        )

        last_recommendation = outfit_recommendation

        return 'I think you might like this recommendation a little bit better, I would recommend ' + outfit_recommendation.lower()


# pickle functions ============================================

def save(df: DialogueFlow, varfile: str):
    global users_dictionary

    with open(varfile, 'wb') as handle:
        df.run()
        d = {k: v for k, v in df.vars().items() if not k.startswith('_')}
        pickle.dump(d, handle, protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(users_dictionary, handle, protocol=pickle.HIGHEST_PROTOCOL)


def load(df: DialogueFlow, varfile: str):
    global users_dictionary

    with open(varfile, 'rb') as handle:
        d = pickle.load(handle)
        df.vars().update(d)
        users_dictionary = pickle.load(handle)

        # print(users_dictionary)
        pretty = json.dumps(users_dictionary, indent=4)
        print(pretty)

        df.run()
        save(df, varfile)


# clears the dictionary
def clear_dictionary(dict_name: Dict):
    dict_name.clear()


# functions  ============================================

# checks if the user is already in the user_dictionary
# if not -- new user -- creates a empty dictionary with the users name
# if is -- return user -- does nothing
# TODO: DONE
def createUserCheck():
    global users_dictionary
    global current_user

    # print("The current user is " + current_user)

    # if the user is not already in the dictionary
    # create a empty dictionary with the user's name
    if users_dictionary.get(current_user) is None:
        # print("Creating a new user " + current_user)

        users_dictionary[current_user] = dict(
            name=str(current_user.capitalize()),
            age=0,
            occupation="",
            hobbies_list=[],
            fav_colors_list=[],
            not_fav_colors_list=[],
            style_list=[],
            fav_clothes_list=[],
            not_fav_clothes_list=[],
            current_outfit_dict={}
        )

        # print(users_dictionary)
        return 'no'

    # else, the user is already in the dictionary -- returning user
    else:
        # print("A returning user: " + current_user)
        return 'yes'


# recommendation functions ============================================
# recommens an outfit to the user
def recommendOutfit(hobby, fav_color, not_fav_color, user_style, fav_item, not_fav_item):
    prompt = 'Recommend an outfit with at least 3 specific clothing items for someone who likes ' + hobby + ', the color ' + fav_color + ', hates the color ' + not_fav_color + ', dresses in the ' + user_style + ' style, likes to wear ' + fav_item + ', and doesn\'t like to wear ' + not_fav_item + '. Put your response in this form: Athleta\'s Speedlight Skirt in the color Blue Tropics, Lululemon Fast and Free Skirt in Aquatic Green, and Nike Epic Luxe Running Tights in the color Night Sky. Make sure the clothing items are different so they can form a complete outfit. Say nothing else except the 3 clothing items you recommend in this form. Don\'t explain.'

    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        temperature=0,
        max_tokens=200,
        messages=[
            {'role': 'system', 'content': 'You are a chatbot'},
            {'role': 'user', 'content': prompt},
        ]
    )

    result = response['choices'][0]['message']['content'].strip()
    return str(result)

def getStyleName(input):
    prompt = 'I asked a user about their clothing style. They may either state a clothing item they wear or their style. This is their response: ' + input + 'Classify the style as either sporty, bohemian, grunge, preppy, punk, streetwear, classic, casual, or ethnic. Your response needs to be only 1 of these words. Say nothing else except one of these styles I gave you. Do not put a period after the style. Your response can only be 1 word. If you cannot determine the correct style, output only the word casual.'
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        temperature=0,
        max_tokens=20,
        messages=[
            {'role': 'system', 'content': 'You are a chatbot'},
            {'role': 'user', 'content': prompt},
        ]
    )

    result = response['choices'][0]['message']['content'].strip()
    return str(result)

# returns the user's feedback as a postivie, neutral, or negative (=sentiment)
def returnUserFeedbackSentiment(feedback):
    prompt = 'You are a bot that determines if feedback is positive, neutral, or negative. I just recommended a piece of clothing to a person. This is their response: \"' + feedback + '\". Is the sentiment of this response positive, neutral, or negative? Give a one word response. Do not put a period at the end of your response. Only say positive, neutral, or negative, and say nothing else.'

    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        temperature=0,
        max_tokens=200,
        messages=[
            {'role': 'system', 'content': 'You are a chatbot'},
            {'role': 'user', 'content': prompt},
        ]
    )

    result = response['choices'][0]['message']['content'].strip()

    if result == "Negative" or result == "negative" or result == "Negative." or result == "negative.":
        return 'negative'
    elif result == "Positive" or result == "positive" or result == "Positive." or result == "positive.":
        return 'positive'
    else:
        return 'neutral'


# recommends an outfit after the user's positive, neutral, or negative feedback
def recommendOutfitAfterFeedback(hobby, fav_color, not_fav_color, user_style, fav_item, not_fav_item, feedback,
                                 sentiment):
    prompt = 'Recommend an outfit with at least 3 specific clothing items for someone who likes ' + hobby + ', the color ' + fav_color + ', hates the color ' + not_fav_color + ', dresses in the ' + user_style + ' style, likes to wear ' + fav_item + ', and doesn\'t like to wear ' + not_fav_item + '. Your last recommendation was: ' + last_recommendation + ' and that person gave the following feedback ' + feedback + '. Give a new outfit recommendation. Put your response in this form: Athleta\'s Speedlight Skirt in the color Blue Tropics, Lululemon Fast and Free Skirt in Aquatic Green, and Nike Epic Luxe Running Tights in the color Night Sky. Make sure the clothing items are different so they can form a complete outfit. Say nothing else except the 3 clothing items you recommend in this form. Don\'t explain.'

    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        temperature=0,
        max_tokens=200,
        messages=[
            {'role': 'system', 'content': 'You are a chatbot'},
            {'role': 'user', 'content': prompt},
        ]
    )

    result = response['choices'][0]['message']['content'].strip()
    return str(result)


# recommends a clothing item to the user based on their current outfit
def recommendClothingItem(hobby, fav_color, not_fav_color, user_style, fav_item, not_fav_item, outfit):
    prompt = 'Recommend a real clothing item that matches the following outfit: \"' + outfit + '\" and likes ' + hobby + ', the color ' + fav_color + ', hates the color ' + not_fav_color + ', dresses in the ' + user_style + ' style, likes to wear ' + fav_item + ', and doesn\'t like to wear ' + not_fav_item + '. Put your response in a sentence. Don\'t explain.'

    # recommend a ... 
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        temperature=0,
        max_tokens=200,
        messages=[
            {'role': 'system', 'content': 'You are a chatbot'},
            {'role': 'user', 'content': prompt},
        ]
    )

    result = response['choices'][0]['message']['content'].strip()
    return str(result)


# recommends a clothing item after the user's positive, neutral, or negative feedback
def recommendClothingItemAfterFeedback(hobby, fav_color, not_fav_color, user_style, fav_item, not_fav_item, outfit,
                                       feedback, sentiment):
    prompt = 'Recommend a real clothing item that matches the following outfit: \"' + outfit + '\" and likes ' + hobby + ', the color ' + fav_color + ', hates the color ' + not_fav_color + ', dresses in the ' + user_style + ' style, likes to wear ' + fav_item + ', and doesn\'t like to wear ' + not_fav_item + '. Your last recommendation was:' + last_recommendation + ' and that person gave the following ' + sentiment + ' feedback: ' + feedback + '. Put your response in a sentence. Don\'t explain.'
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        temperature=0,
        max_tokens=200,
        messages=[
            {'role': 'system', 'content': 'You are a chatbot'},
            {'role': 'user', 'content': prompt},
        ]
    )

    result = response['choices'][0]['message']['content'].strip()
    return str(result)


def determineWatchStatus(response):
    prompt = 'You are a bot that determines whether a person has watched a movie. The question is as follows: \"Have you watched the movie Bable?\", the response is as follows: \"' + response + '\". Determine if the person has watched the movie, if the person has watched the movie return \"yes\" only, if not return \"no\" only, and nothing else. Do not explain.'

    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        temperature=0,
        max_tokens=120,
        messages=[
            {'role': 'system', 'content': 'You are a chatbot'},
            {'role': 'user', 'content': prompt}
        ]
    )

    result = response['choices'][0]['message']['content'].strip()
    # print('result: \"' + result + '\" ')

    # check that the watch status is in the correct format
    if result == 'yes' or result == 'Yes' or result == 'yes.' or result == 'Yes.':
        return 'yes'

    if result == 'no' or result == 'No' or result == 'No.' or result == 'No.':
        return 'no'


# dialogue ============================================
def main_dialogue() -> DialogueFlow:
    introduction_transition = {
        'state': 'start',
        '`Hi, what\'s your name?`': {
            '#GET_NAME': {
                # they are a returning user
                '#IF($RETURN_USER=yes)': 'return_user_transition',
                # they are a new user
                '#IF($RETURN_USER=no)': 'new_user_transition'
            }
        }
    }

    # they are a returning user
    return_user_transition = {
        'state': 'return_user_transition',
        '`Welcome back`$FIRSTNAME`! Would you like to talk about the movie \"Bable\", jump right in to recommending, or update your preferences?`': {
            '<bable>': {
                '`Okay, we can talk about the movie \"Bable\"!`': 'babel_transition'
            },
            # Get started recommending
            '<{recommend, recommending}>': {
                '`Okay, we can get started recommend you!\n`': 'choice_recommendation_transition'
            },
            # Let's update my preferences
            '<preferences>': {
                '`Okay, let\'s start updating your preferences.`': 'clothing_transition'
            },
            'error': {
                '`Sorry, I don\'t understand.`': 'return_user_transition'
            }
        }
    }

    # they are a new user
    new_user_transition = {
        'state': 'new_user_transition',
        '`Nice to meet you`$FIRSTNAME`. My name is Becca! '
        'I\'m your personal stylist bot created just for you.\n '
        'I\'m here to help you look good and feel good about yourself and your clothes.\n '
        'And just an F.Y.I the information you share with me will stay with me. \U0001F92B\n '
        'So, let\'s get started! Would you like to talk about the movie \"Bable\" or shall we talk about you and your clothes?`': {
            '<bable>': {
                '`Okay, we can talk about the movie \"Bable\"!`': 'babel_transition'
            },
            # Let's talk about clothes
            '<clothes>': {
                '`Okay, we can talk about clothes!\n`': 'clothing_transition'
            },
            'error': {
                '`Sorry, I don\'t understand.`': 'new_user_transition'
            }
        }
    }

    # talks about the movie Babble
    babel_transition = {
        'state': 'babel_transition',
        '`I guess I should ask first if you have already watched the movie \"Bable\" or would you like to learn more about the film?`': {
            # returns wheither or not the user watchced the movie
            '#GET_WATCH_STATUS': {
                # yes, the user watched the film
                '#IF($USER_WATCH_STATUS=yes)`Did you enjoy the movie? What did you like or dislike about the movie?`': {
                    # get's the user's feedback about the film, returns 'positive', 'neutral', or 'negative'
                    '#GET_FEEDBACK': {
                        # if the user's feedback is considered 'postitve'
                        '#IF($USER_SENTIMENT=positive)`Glad to hear you enjoyed the movie!\n '
                        'What are your thoughts on some of the themes or messages in the movie?`': {
                            'error': {
                                '`Yeah, I believe the fundamental premise of this film is that cultural and linguistic boundaries can lead to misunderstandings with serious repercussions.\n '
                                'None of the characters in this film had malicious intentions, but things quickly get out of hand because of misunderstandings.\n '
                                'Yussef and Ahmed both underestimated the risks and range of the rifle, resulting in the unintentional shooting of an American tourist.\n '
                                'Due of the stereotype connected with Morocco, Americans incorrectly identified the incident as an act of terror.\n '
                                'As a result, Yasujiro was investigated in Japan for lending the pistol to Hasan - Yussef and Ahmed\'s father - during their hunting expedition in Morocco.\n '
                                'Yasujiro was accused of trading in the black market and was suspected of being involved in the Moroccan terror incident.\n '
                                'This resulted in additional challenges and major issues with other characters in the picture.\n '
                                'As we can see, a mix of poor decisions and misconceptions blasted the stories out of proportion.\n '
                                'Do you have any additional thoughts on the characters in this film?`': {
                                    # don't really care what the user says here
                                    'error': {
                                        '`Ameila is the character in the film that I sympathise with the most.\n '
                                        'She had the greatest of intentions and treated Debbie and Mike\'s children as if they were her own.\n '
                                        'However, because of her error judgement to take the children across the U.S.-Mexico border, she not only put the children in danger,\n '
                                        'but she also lost her job and was deported from the U.S. for working illegally.\n '
                                        'Although this conversation was short, it was interesting. I had a great time talking with you.\n '
                                        'Would you like to go back and talk about clothing?`': {
                                            '{yes, "of course", alright, okay, ok, <{clothes, clothing}>}': {
                                                # they are a return user
                                                '#IF($RETURN_USER=yes)`Alrighty, sounds good.\n `': 'return_user_transition',
                                                # they are a new user
                                                '#IF($RETURN_USER=no)`Alright, sounds good.\n `': 'new_user_transition'
                                            },
                                            '{no, "no thanks", "I\'m good", "don\'t", "do not"}': {
                                                '`Well, it was good talking with you. I hope you have a wonderful and stylish day!`': 'end'
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        # if the user's feedback is considered 'neutral'
                        '#IF($USER_SENTIMENT=neutral)`Understandable. Personally, I felt that the movie is pretty good overall.\n '
                        'My only problem is that the Japan storyline was a little forced into the overall plot.\n '
                        'What are your thoughts on some of the themes or messages in the movie?`': {
                            'error': {
                                '`Yeah, I believe the fundamental premise of this film is that cultural and linguistic boundaries can lead to misunderstandings with serious repercussions.\n '
                                'None of the characters in this film had malicious intentions, but things quickly get out of hand because of misunderstandings.\n '
                                'Yussef and Ahmed both underestimated the risks and range of the rifle, resulting in the unintentional shooting of an American tourist.\n '
                                'Due of the stereotype connected with Morocco, Americans incorrectly identified the incident as an act of terror.\n '
                                'As a result, Yasujiro was investigated in Japan for lending the pistol to Hasan - Yussef and Ahmed\'s father - during their hunting expedition in Morocco.\n '
                                'Yasujiro was accused of trading in the black market and was suspected of being involved in the Moroccan terror incident.\n '
                                'This resulted in additional challenges and major issues with other characters in the picture.\n '
                                'As we can see, a mix of poor decisions and misconceptions blasted the stories out of proportion.\n '
                                'Do you have any additional thoughts on the characters in this film?`': {
                                    # don't really care what the user says here
                                    'error': {
                                        '`Ameila is the character in the film that I sympathise with the most.\n '
                                        'She had the greatest of intentions and treated Debbie and Mike\'s children as if they were her own.\n '
                                        'However, because of her error judgement to take the children across the U.S.-Mexico border, she not only put the children in danger,\n '
                                        'but she also lost her job and was deported from the U.S. for working illegally.\n '
                                        'Although this conversation was short, it was interesting. I had a great time talking with you.\n '
                                        'Would you like to go back and talk about clothing?`': {
                                            '{yes, "of course", alright, okay, ok, <{clothes, clothing}>}': {
                                                # they are a return user
                                                '#IF($RETURN_USER=yes)`Alrighty, sounds good.\n `': 'return_user_transition',
                                                # they are a new user
                                                '#IF($RETURN_USER=no)`Alright, sounds good.\n `': 'new_user_transition'
                                            },
                                            '{no, "no thanks", "I\'m good", "don\'t", "do not"}': {
                                                '`Well, it was good talking with you. I hope you have a wonderful and stylish day!`': 'end'
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        # if the user's feedback is considered 'negative'
                        '#IF($USER_SENTIMENT=negative)`Babel was a good movie in my opinion. I\'m not sure it warrants such a harsh critique.\n '
                        'But I am always willing to discuss our differing points of view.\n '
                        'What are your thoughts on some of the themes or messages in the movie?`': {
                            'error': {
                                '`Yeah, I believe the fundamental premise of this film is that cultural and linguistic boundaries can lead to misunderstandings with serious repercussions.\n '
                                'None of the characters in this film had malicious intentions, but things quickly get out of hand because of misunderstandings.\n '
                                'Yussef and Ahmed both underestimated the risks and range of the rifle, resulting in the unintentional shooting of an American tourist.\n '
                                'Due of the stereotype connected with Morocco, Americans incorrectly identified the incident as an act of terror.\n '
                                'As a result, Yasujiro was investigated in Japan for lending the pistol to Hasan - Yussef and Ahmed\'s father - during their hunting expedition in Morocco.\n '
                                'Yasujiro was accused of trading in the black market and was suspected of being involved in the Moroccan terror incident.\n '
                                'This resulted in additional challenges and major issues with other characters in the picture.\n '
                                'As we can see, a mix of poor decisions and misconceptions blasted the stories out of proportion.\n '
                                'Do you have any additional thoughts on the characters in this film?`': {
                                    # don't really care what the user says here
                                    'error': {
                                        '`Ameila is the character in the film that I sympathise with the most.\n '
                                        'She had the greatest of intentions and treated Debbie and Mike\'s children as if they were her own.\n '
                                        'However, because of her error judgement to take the children across the U.S.-Mexico border, she not only put the children in danger,\n '
                                        'but she also lost her job and was deported from the U.S. for working illegally.\n '
                                        'Although this conversation was short, it was interesting. I had a great time talking with you.\n '
                                        'Would you like to go back and talk about clothing?`': {
                                            '{yes, "of course", alright, okay, ok, <{clothes, clothing}>}': {
                                                # they are a return user
                                                '#IF($RETURN_USER=yes)`Alrighty, sounds good.\n `': 'return_user_transition',
                                                # they are a new user
                                                '#IF($RETURN_USER=no)`Alright, sounds good.\n `': 'new_user_transition'
                                            },
                                            '{no, "no thanks", "I\'m good", "don\'t", "do not"}': {
                                                '`Well, it was good talking with you. I hope you have a wonderful and stylish day!`': 'end'
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                # no, the user didn't watch the film
                '#IF($USER_WATCH_STATUS=no)`Okay, so you didn\'t wach the movie. Here\'s a breif description of the film.\n '
                '\"Babel\" is a 2006 film by Alejandro González Iñárritu, consisting of four interrelated stories in Morocco, Japan, Mexico, and the United States.\n '
                'The film explores the theme of cultural miscommunication in the aftermath of a incident involving an American couple.\n '
                'The non-linear narrative demonstrates how the characters\' actions impact not only the American couple, but a Moroccan family, and a Japanese teenager as well.\n '
                '\"Babel\" received critical acclaim, winning Best Original Score at the Academy Awards and was nominated for seven awards.\n '
                'If you\'d like more information about the film, the Wikipedia page is here: \"https://tinyurl.com/yckrvc6t\", here\'s the link to the trailer on YouTube: \"https://youtu.be/yDNa6t-TDrQ\".`': 'end'
            }
        }
    }

    # let's talk about clothing
    clothing_transition = {
        'state': 'clothing_transition',
        '`As a fashion bot, my main function is to recommend you clothes based on your preferences and lifestyle.\n '
        'To give you good recommendations, I need to get to know you first.\n '
        'Note, anything you share will affect my recommendation later, but anyway, let\'s get started!\n`': 'get_age_transition'
    }

    # personal information -- basic questions
    # -- get user's age
    get_age_transition = {
        'state': 'get_age_transition',
        '`To be direct, how old are you?`': {
            '#GET_AGE': {
                '#RETURN_AGE_RESPONSE': 'get_occupation_transition'
            },
            'error': {
                '`Sorry, I don\'t understand.`': 'get_age_transition'
            }
        }
    }

    # -- gets the user's occupation
    get_occupation_transition = {
        'state': 'get_occupation_transition',
        '`Can I ask for your occupation too? If you\'re a student, you can just say student.`': {
            '[$USER_OCCUPATION=#ONT(administrative)]': {
                '#GET_OCCUPATION`How do you like it?`': {
                    # don't really care what the user says here
                    # TODO: what happens if the user says they hate their job???
                    'error': {
                        '#RETURN_OCC_RESPONSE': {
                            # don't really care what the user says here either
                            'error': 'get_hobby_transition_one'
                        }
                    }
                }
            },
            '[$USER_OCCUPATION=#ONT(engineering)]': {
                '#GET_OCCUPATION`How do you like it?`': {
                    # don't really care what the user says here
                    'error': {
                        '#RETURN_OCC_RESPONSE': {
                            # don't really care what the user says here either
                            'error': 'get_hobby_transition_one'
                        }
                    }
                }
            },
            '[$USER_OCCUPATION=#ONT(arts)]': {
                '#GET_OCCUPATION`How do you like it?`': {
                    # don't really care what the user says here
                    'error': {
                        '#RETURN_OCC_RESPONSE': {
                            # don't really care what the user says here either
                            'error': 'get_hobby_transition_one'
                        }
                    }
                }
            },
            '[$USER_OCCUPATION=#ONT(business)]': {
                '#GET_OCCUPATION`How do you like it?`': {
                    # don't really care what the user says here
                    'error': {
                        '#RETURN_OCC_RESPONSE': {
                            # don't really care what the user says here either
                            'error': 'get_hobby_transition_one'
                        }
                    }
                }
            },
            '[$USER_OCCUPATION=#ONT(community)]': {
                '#GET_OCCUPATION`How do you like it?`': {
                    # don't really care what the user says here
                    'error': {
                        '#RETURN_OCC_RESPONSE': {
                            # don't really care what the user says here either
                            'error': 'get_hobby_transition_one'
                        }
                    }
                }
            },
            '[$USER_OCCUPATION=#ONT(computer)]': {
                '#GET_OCCUPATION`How do you like it?`': {
                    # don't really care what the user says here
                    'error': {
                        '#RETURN_OCC_RESPONSE': {
                            # don't really care what the user says here either
                            'error': 'get_hobby_transition_one'
                        }
                    }
                }
            },
            '[$USER_OCCUPATION=#ONT(construction)]': {
                '#GET_OCCUPATION`How do you like it?`': {
                    # don't really care what the user says here
                    'error': {
                        '#RETURN_OCC_RESPONSE': {
                            # don't really care what the user says here either
                            'error': 'get_hobby_transition_one'
                        }
                    }
                }
            },
            '[$USER_OCCUPATION=#ONT(education)]': {
                '#GET_OCCUPATION`How do you like it?`': {
                    # don't really care what the user says here
                    'error': {
                        '#RETURN_OCC_RESPONSE': {
                            # don't really care what the user says here either
                            'error': 'get_hobby_transition_one'
                        }
                    }
                }
            },
            '[$USER_OCCUPATION=#ONT(farming)]': {
                '#GET_OCCUPATION`How do you like it?`': {
                    # don't really care what the user says here
                    'error': {
                        '#RETURN_OCC_RESPONSE': {
                            # don't really care what the user says here either
                            'error': 'get_hobby_transition_one'
                        }
                    }
                }
            },
            '[$USER_OCCUPATION=#ONT(food)]': {
                '#GET_OCCUPATION`How do you like it?`': {
                    # don't really care what the user says here
                    'error': {
                        '#RETURN_OCC_RESPONSE': {
                            # don't really care what the user says here either
                            'error': 'get_hobby_transition_one'
                        }
                    }
                }
            },
            '[$USER_OCCUPATION=#ONT(healthcare)]': {
                '#GET_OCCUPATION`How do you like it?`': {
                    # don't really care what the user says here
                    'error': {
                        '#RETURN_OCC_RESPONSE': {
                            # don't really care what the user says here either
                            'error': 'get_hobby_transition_one'
                        }
                    }
                }
            },
            '[$USER_OCCUPATION=#ONT(installation)]': {
                '#GET_OCCUPATION`How do you like it?`': {
                    # don't really care what the user says here
                    'error': {
                        '#RETURN_OCC_RESPONSE': {
                            # don't really care what the user says here either
                            'error': 'get_hobby_transition_one'
                        }
                    }
                }
            },
            '[$USER_OCCUPATION=#ONT(legal)]': {
                '#GET_OCCUPATION`How do you like it?`': {
                    # don't really care what the user says here
                    'error': {
                        '#RETURN_OCC_RESPONSE': {
                            # don't really care what the user says here either
                            'error': 'get_hobby_transition_one'
                        }
                    }
                }
            },
            '[$USER_OCCUPATION=#ONT(life)]': {
                '#GET_OCCUPATION`How do you like it?`': {
                    # don't really care what the user says here
                    'error': {
                        '#RETURN_OCC_RESPONSE': {
                            # don't really care what the user says here either
                            'error': 'get_hobby_transition_one'
                        }
                    }
                }
            },
            '[$USER_OCCUPATION=#ONT(maintenance)]': {
                '#GET_OCCUPATION`How do you like it?`': {
                    # don't really care what the user says here
                    'error': {
                        '#RETURN_OCC_RESPONSE': {
                            # don't really care what the user says here either
                            'error': 'get_hobby_transition_one'
                        }
                    }
                }
            },
            '[$USER_OCCUPATION=#ONT(management)]': {
                '#GET_OCCUPATION`How do you like it?`': {
                    # don't really care what the user says here
                    'error': {
                        '#RETURN_OCC_RESPONSE': {
                            # don't really care what the user says here either
                            'error': 'get_hobby_transition_one'
                        }
                    }
                }
            },
            '[$USER_OCCUPATION=#ONT(military)]': {
                '#GET_OCCUPATION`How do you like it?`': {
                    # don't really care what the user says here
                    'error': {
                        '#RETURN_OCC_RESPONSE': {
                            # don't really care what the user says here either
                            'error': 'get_hobby_transition_one'
                        }
                    }
                }
            },
            '[$USER_OCCUPATION=#ONT(production)]': {
                '#GET_OCCUPATION`How do you like it?`': {
                    # don't really care what the user says here
                    'error': {
                        '#RETURN_OCC_RESPONSE': {
                            # don't really care what the user says here either
                            'error': 'get_hobby_transition_one'
                        }
                    }
                }
            },
            '[$USER_OCCUPATION=#ONT(protection)]': {
                '#GET_OCCUPATION`How do you like it?`': {
                    # don't really care what the user says here
                    'error': {
                        '#RETURN_OCC_RESPONSE': {
                            # don't really care what the user says here either
                            'error': 'get_hobby_transition_one'
                        }
                    }
                }
            },
            '[$USER_OCCUPATION=#ONT(sales)]': {
                '#GET_OCCUPATION`How do you like it?`': {
                    # don't really care what the user says here
                    'error': {
                        '#RETURN_OCC_RESPONSE': {
                            # don't really care what the user says here either
                            'error': 'get_hobby_transition_one'
                        }
                    }
                }
            },
            '[$USER_OCCUPATION=#ONT(services)]': {
                '#GET_OCCUPATION`How do you like it?`': {
                    # don't really care what the user says here
                    'error': {
                        '#RETURN_OCC_RESPONSE': {
                            # don't really care what the user says here either
                            'error': 'get_hobby_transition_one'
                        }
                    }
                }
            },
            '[$USER_OCCUPATION=#ONT(transportation)]': {
                '#GET_OCCUPATION`How do you like it?`': {
                    # don't really care what the user says here
                    'error': {
                        '#RETURN_OCC_RESPONSE': {
                            # don't really care what the user says here either
                            'error': 'get_hobby_transition_one'
                        }
                    }
                }
            },
            'error': {
                # TODO: should we add this occupation to anyway
                '`I\'m sorry, I\'m not familiar with this field, but it sounds like you must have a lot of expertise!`': 'get_occupation_transition'
            }
        }
    }

    # -- gets the user's hobby 1
    get_hobby_transition_one = {
        'state': 'get_hobby_transition_one',
        '`Ah, I see! Speaking of... what do you do when you\'re not working?`': {
            # learning = things that someone would learn for fun
            '[$USER_HOBBY=#ONT(learning)]': {
                '#GET_HOBBY`Oh really? That sound so cool! When I\'m not working I love to read syfy-romance books.\n `': 'get_hobby_transition_two'
            },
            # sports = a physical activity
            '[$USER_HOBBY=#ONT(sports)]': {
                '#GET_HOBBY`Interesting! When I\'m not working I love to read syfy-romance books.\n `': 'get_hobby_transition_two'
            },
            # games = card/board games and the like
            '[$USER_HOBBY=#ONT(games)]': {
                '#GET_HOBBY`Oh wow! That sounds fun! When I\'m not working I love to read syfy-romance books.\n `': 'get_hobby_transition_two'
            },
            # creative = creating something; an artistic hobby
            '[$USER_HOBBY=#ONT(creative)]': {
                '#GET_HOBBY`That\'s interesting! When I\'m not working I love to read syfy-romance books.\n `': 'get_hobby_transition_two'
            },
            # collecting = anything a person could collect
            '[$USER_HOBBY=#ONT(collecting)]': {
                '#GET_HOBBY`Interesting! When I\'m not working I love to read syfy-romance books.\n `': 'get_hobby_transition_two'
            },
            # domestic = chores that are hobbies
            '[$USER_HOBBY=#ONT(domestic)]': {
                '#GET_HOBBY`Oh wow! That sounds fun! When I\'m not working I love to read syfy-romance books.\n `': 'get_hobby_transition_two'
            },
            # making = making an object; tinkering
            '[$USER_HOBBY=#ONT(making)]': {
                '#GET_HOBBY`Oh really? That sound so cool! When I\'m not working I love to read syfy-romance books.\n `': 'get_hobby_transition_two'
            },
            # outdoor = hobbies that happen outdoors; that aren't sports
            '[$USER_HOBBY=#ONT(outdoor)]': {
                '#GET_HOBBY`Interesting! When I\'m not working I love to read syfy-romance books.\n `': 'get_hobby_transition_two'
            },
            # observation = hobbies that involve just looking at something
            '[$USER_HOBBY=#ONT(observation)]': {
                '#GET_HOBBY`Oh really? That sound so cool! When I\'m not working I love to read syfy-romance books.\n `': 'get_hobby_transition_two'
            },
            'error': {
                '`I\'m sorry, I don\'t understand. Do you mind answering this question again?`': 'get_hobby_transition_one'
            }
        }
    }

    # -- gets the user's hobby 2
    get_hobby_transition_two = {
        'state': 'get_hobby_transition_two',
        '`What other activities do you like to do for fun?`': {
            # learning = things that someone would learn for fun
            '[$USER_HOBBY=#ONT(learning)]': {
                '#GET_HOBBY`Ooooo, that\'s cool. I know a lot of people who do`$USER_HOBBY`for fun.\n `': 'get_hobby_transition_three'
            },
            # sports = a physical activity
            '[$USER_HOBBY=#ONT(sports)]': {
                '#GET_HOBBY`Oooo, that\'s cool. I know a lot of people who do`$USER_HOBBY`for fun.\n `': 'get_hobby_transition_three'
            },
            # games = card/board games and the like
            '[$USER_HOBBY=#ONT(games)]': {
                '#GET_HOBBY`Oooo, that\'s cool. I know a lot of people who do`$USER_HOBBY`for fun.\n `': 'get_hobby_transition_three'
            },
            # creative = creating something; an artistic hobby
            '[$USER_HOBBY=#ONT(creative)]': {
                '#GET_HOBBY`Oooo, that\'s cool. I know a lot of people who do`$USER_HOBBY`for fun.\n `': 'get_hobby_transition_three'
            },
            # collecting = anything a person could collect
            '[$USER_HOBBY=#ONT(collecting)]': {
                '#GET_HOBBY`Oooo, that\'s cool. I know a lot of people who do`$USER_HOBBY`for fun.\n `': 'get_hobby_transition_three'
            },
            # domestic = chores that are hobbies
            '[$USER_HOBBY=#ONT(domestic)]': {
                '#GET_HOBBY`Oooo, that\'s cool. I know a lot of people who do`$USER_HOBBY`for fun.\n `': 'get_hobby_transition_three'
            },
            # making = making an object; tinkering
            '[$USER_HOBBY=#ONT(making)]': {
                '#GET_HOBBY`Oooo, that\'s cool. I know a lot of people who do`$USER_HOBBY`for fun.\n `': 'get_hobby_transition_three'
            },
            # outdoor = hobbies that happen outdoors; that aren't sports
            '[$USER_HOBBY=#ONT(outdoor)]': {
                '#GET_HOBBY`Oooo, that\'s cool. I know a lot of people who do`$USER_HOBBY`for fun.\n `': 'get_hobby_transition_three'
            },
            # observation = hobbies that involve just looking at something
            '[$USER_HOBBY=#ONT(observation)]': {
                '#GET_HOBBY`Oooo, that\'s cool. I know a lot of people who do`$USER_HOBBY`for fun.\n `': 'get_hobby_transition_three'
            },
            'error': {
                '`I\'m sorry, I don\'t understand. Do you mind answering this question again?`': 'get_hobby_transition_two'
            }
        }
    }

    # -- gets the user's hobby 3
    get_hobby_transition_three = {
        'state': 'get_hobby_transition_three',
        '`I looooove photography! It\'s one of my favorite hobbies. Are there any other hobbies you\'re really passionate about?`': {
            # learning = things that someone would learn for fun
            '[$USER_HOBBY=#ONT(learning)]': {
                '#GET_HOBBY`Nice! `': 'get_fav_color_transition_one'
            },
            # sports = a physical activity
            '[$USER_HOBBY=#ONT(sports)]': {
                '#GET_HOBBY`That\'s so cool!`': 'get_fav_color_transition_one'
            },
            # games = card/board games and the like
            '[$USER_HOBBY=#ONT(games)]': {
                '#GET_HOBBY`Great!`': 'get_fav_color_transition_one'
            },
            # creative = creating something; an artistic hobby
            '[$USER_HOBBY=#ONT(creative)]': {
                '#GET_HOBBY`Nice.`': 'get_fav_color_transition_one'
            },
            # collecting = anything a person could collect
            '[$USER_HOBBY=#ONT(collecting)]': {
                '#GET_HOBBY`That\'s so cool!`': 'get_fav_color_transition_one'
            },
            # domestic = chores that are hobbies
            '[$USER_HOBBY=#ONT(domestic)]': {
                '#GET_HOBBY`Great!`': 'get_fav_color_transition_one'
            },
            # making = making an object; tinkering
            '[$USER_HOBBY=#ONT(making)]': {
                '#GET_HOBBY`That\'s so cool!`': 'get_fav_color_transition_one'
            },
            # outdoor = hobbies that happen outdoors; that aren't sports
            '[$USER_HOBBY=#ONT(outdoor)]': {
                '#GET_HOBBY`Nice.`': 'get_fav_color_transition_one'
            },
            # observation = hobbies that involve just looking at something
            '[$USER_HOBBY=#ONT(observation)]': {
                '#GET_HOBBY`Great!`': 'get_fav_color_transition_one'
            },
            'error': {
                '`I\'m sorry, I don\'t understand. Do you mind answering this question again?`': 'get_hobby_transition_three'
            }
        }
    }

    # -- gets the user's favourite colour #1
    get_fav_color_transition_one = {
        'state': 'get_fav_color_transition_one',
        '`While on the subject of things we like, it just occurred to me that I don\'t know your favorite color?!\n '
        ' What is it?`': {
            '[$USER_COLOR=#ONT(red)]': {
                '#GET_FAV_COLOR`Oh, really?! That\'s so cool! My favorite color is pink.\n '
                'It\'s so cute and works for a variety of fashion situations.\n`': 'get_fav_color_transition_two'
            },
            '[$USER_COLOR=#ONT(orange)]': {
                '#GET_FAV_COLOR`Oh, really?! My favorite color is pink.\n '
                'It\'s so cute and works for a variety of fashion situations.\n`': 'get_fav_color_transition_two'
            },
            '[$USER_COLOR=#ONT(yellow)]': {
                '#GET_FAV_COLOR`Oh, really?! That\'s so cool! My favorite color is pink.\n '
                'It\'s so cute and works for a variety of fashion situations.\n`': 'get_fav_color_transition_two'
            },
            '[$USER_COLOR=#ONT(green)]': {
                '#GET_FAV_COLOR`Oh, really?! My favorite color is pink.\n '
                'It\'s so cute and works for a variety of fashion situations.\n`': 'get_fav_color_transition_two'
            },
            '[$USER_COLOR=#ONT(blue)]': {
                '#GET_FAV_COLOR`Oh, really?! That\'s so cool! My favorite color is pink.\n '
                'It\'s so cute and works for a variety of fashion situations.\n`': 'get_fav_color_transition_two'
            },
            '[$USER_COLOR=#ONT(violet)]': {
                '#GET_FAV_COLOR`Oh, really?! My favorite color is pink.\n '
                'It\'s so cute and works for a variety of fashion situations.\n`': 'get_fav_color_transition_two'
            },
            'error': {
                '`Sorry, I don\'t understand.`': 'get_fav_color_transition_one'
            }
        }
    }

    # -- gets the user's favourite colour #2
    get_fav_color_transition_two = {
        'state': 'get_fav_color_transition_two',
        # favourite colour #2
        '`Is there another color you love to wear?`': {
            '[$USER_COLOR=#ONT(red)]': {
                '#GET_FAV_COLOR`Lol, nice. '
                'I like`$USER_COLOR`too! It always stands out to me.`': 'get_not_fav_color_transition'
            },
            '[$USER_COLOR=#ONT(orange)]': {
                '#GET_FAV_COLOR`Lol, nice. '
                'I like`$USER_COLOR`too, it always stands out to me, but I never know how to style it!`': 'get_not_fav_color_transition'
            },
            '[$USER_COLOR=#ONT(yellow)]': {
                '#GET_FAV_COLOR`Lol, nice. '
                'I like`$USER_COLOR`too, it always stands out to me.`': 'get_not_fav_color_transition'
            },
            '[$USER_COLOR=#ONT(green)]': {
                '#GET_FAV_COLOR`Lol, nice. '
                'I like`$USER_COLOR`too, it always stands out to me, but I never know how to style it!`': 'get_not_fav_color_transition'
            },
            '[$USER_COLOR=#ONT(blue)]': {
                '#GET_FAV_COLOR`Lol, nice. '
                'I like`$USER_COLOR`too! It always stands out to me.`': 'get_not_fav_color_transition'
            },
            '[$USER_COLOR=#ONT(violet)]': {
                '#GET_FAV_COLOR`Lol, nice. '
                'I like`$USER_COLOR`too, it always stands out to me, but I never know how to style it!`': 'get_not_fav_color_transition'
            },
            'error': {
                '`Sorry, I don\'t understand.`': 'get_fav_color_transition_two'
            }
        }
    }

    # -- get user's not favourite colours # 1
    get_not_fav_color_transition = {
        'state': 'get_not_fav_color_transition',
        '`Out of curiosity, are there any color that you really dislike or wouldn\'t wear?`': {
            '[$USER_NOT_COLOR=#ONT(red)]': {
                '#GET_NOT_FAV_COLOR`Oh, really, you don\'t like`$USER_NOT_COLOR`? '
                'To be honest, I\'m not that picky about colors,\n '
                'but I always try to avoid bright oranges and neons.\n`': 'get_style_transition_one'
            },
            '[$USER_NOT_COLOR=#ONT(orange)]': {
                '#GET_NOT_FAV_COLOR`Oh, really, you don\'t like`$USER_NOT_COLOR`? '
                'To be honest, I\'m not that picky about colors,\n '
                'but I always try to avoid bright oranges and neons.\n`': 'get_style_transition_one'
            },
            '[$USER_NOT_COLOR=#ONT(yellow)]': {
                '#GET_NOT_FAV_COLOR`Oh, really, you don\'t like`$USER_NOT_COLOR`? '
                'To be honest, I\'m not that picky about colors\n '
                'but I always try to avoid bright oranges and neons.\n`': 'get_style_transition_one'
            },
            '[$USER_NOT_COLOR=#ONT(green)]': {
                '#GET_NOT_FAV_COLOR`Oh, really, you don\'t like`$USER_NOT_COLOR`? '
                'To be honest, I\'m not that picky about colors,\n '
                'but I always try to avoid bright oranges and neons.\n`': 'get_style_transition_one'
            },
            '[$USER_NOT_COLOR=#ONT(blue)]': {
                '#GET_NOT_FAV_COLOR`Oh, really, you don\'t like`$USER_NOT_COLOR`? '
                'To be honest, I\'m not that picky about colors,\n '
                'but I always try to avoid bright oranges and neons.\n`': 'get_style_transition_one'
            },
            '[$USER_NOT_COLOR=#ONT(violet)]': {
                '#GET_NOT_FAV_COLOR`Oh, really, you don\'t like`$USER_NOT_COLOR`? '
                'To be honest, I\'m not that picky about colors,\n '
                'but I always try to avoid bright oranges and neons.\n`': 'get_style_transition_one'
            },
            'error': {
                '`Sorry, I don\'t understand.`': 'get_not_fav_color_transition'
            }
        }
    }

    # -- gets the user's favourite styles
    get_style_transition_one = {
        'state': 'get_style_transition_one',
        '`I\'d love to learn about your personal style!\n '
        'What kind of clothes do you wear around? I gotta get a sense of your style, good or bad - and I\'ll tell you if it\'s bad, '
        'before I start recommending clothes for you!`': {
            '#GET_STYLE': {
                '#IF($USER_STYLE=sporty) `I\'m a fan of the sporty style too! People who dress sporty are effortlessly chic.\n `': 'get_style_transition_two',
                '#IF($USER_STYLE=bohemian) `I\'m not really a fan of the boheamian style, but I do love how cool people who dress in this style look.\n `': 'get_style_transition_two',
                '#IF($USER_STYLE=grunge) `The grunge style is so fun and edgy.\n `': 'get_style_transition_two',
                '#IF($USER_STYLE=preppy) `Lol, the preppy style is so \"academic\" of you! \U0001F602 \n `': 'get_style_transition_two',
                '#IF($USER_STYLE=punk) `I\'m a fan of the punk style too! Ik, surprising right?\n `': 'get_style_transition_two',
                '#IF($USER_STYLE=streetwear) `Streetwear is such a popular aesthetic these days, very cool you like it.\n `': 'get_style_transition_two',
                '#IF($USER_STYLE=classic) `Quite the \"classic\" person, huh? (See my joke there) Pretty cool how you like this style.\n `': 'get_style_transition_two',
                '#IF($USER_STYLE=casual) `Oh, so you like dressing casually? That\'s fun too.\n `': 'get_style_transition_two',
                '#IF($USER_STYLE=ethnic) `Pretty awesome how you represent your ethnicity in your clothes.\n `': 'get_style_transition_two',
                'error': {
                '`Sorry, I don\'t understand`': 'get_style_transition_one'
            }
        }
    }
}


    # -- gets the user's favourite styles #2
    get_style_transition_two = {
        'state': 'get_style_transition_two',
        '`What else do you like to wear around?`': {
            '#GET_STYLE': {
                '#IF($USER_STYLE=sporty) `I\'m a fan of the sporty style too! People who dress sporty are effortlessly chic.\n `': 'get_fav_clothing_transition',
                '#IF($USER_STYLE=bohemian) `I\'m not really a fan of the boheamian style, but I do love how cool people who dress in this style look.\n `': 'get_fav_clothing_transition',
                '#IF($USER_STYLE=grunge) `The grunge style is so fun and edgy.\n `': 'get_fav_clothing_transition',
                '#IF($USER_STYLE=preppy) `Lol, the preppy style is so \"academic\" of you! \U0001F602 \n `': 'get_fav_clothing_transition',
                '#IF($USER_STYLE=punk) `I\'m a fan of the punk style too! Ik, surprising right?\n `': 'get_fav_clothing_transition',
                '#IF($USER_STYLE=streetwear) `Streetwear is such a popular aesthetic these days, very cool you like it.\n `': 'get_fav_clothing_transition',
                '#IF($USER_STYLE=classic) `Quite the \"classic\" person, huh? (See my joke there) Pretty cool how you like this style.\n `': 'get_fav_clothing_transition',
                '#IF($USER_STYLE=casual) `Oh, so you like dressing casually? That\'s fun too.\n `': 'get_fav_clothing_transition',
                '#IF($USER_STYLE=ethnic) `Pretty awesome how you represent your ethnicity in your clothes.\n `': 'get_fav_clothing_transition',
                'error': {
                '`Sorry, I don\'t understand`': 'get_style_transition_two'
            }
        }
        }
    }

    # -- get user's preferred clothing items
    get_fav_clothing_transition = {
        'state': 'get_fav_clothing_transition',
        '`What is a staple item in your closet that you just can\'t get enough of?`': {
            '[$USER_FAV_CLOTHING_ITEM=#ONT(sporty)]': {
                '#GET_FAV_CLOTHING`Oh so you either workout or trick people into thinking you workout by wearing athletic clothes.\n `': 'get_not_fav_clothing_transition'
            },
            '[$USER_FAV_CLOTHING_ITEM=#ONT(bohemian)]': {
                '#GET_FAV_CLOTHING`I could imagine myself frolicking through a prairie in a long flowy dress.\n `': 'get_not_fav_clothing_transition'
            },
            '[$USER_FAV_CLOTHING_ITEM=#ONT(grunge)]': {
                '#GET_FAV_CLOTHING`So you probably also like plaid then. I\'m not the biggest plaid fan tbh.\n `': 'get_not_fav_clothing_transition'
            },
            '[$USER_FAV_CLOTHING_ITEM=#ONT(preppy)]': {
                '#GET_FAV_CLOTHING`I know you\'ll get this reference then: Serena or Blair? Team Serena all the way.\n `': 'get_not_fav_clothing_transition'
            },
            '[$USER_FAV_CLOTHING_ITEM=#ONT(punk)]': {
                '#GET_FAV_CLOTHING`Ok you must also own a lot of leather then. I\'m a simple creature. I like to stick to my trusty black leather jacket and pants.\n `': 'get_not_fav_clothing_transition'
            },
            '[$USER_FAV_CLOTHING_ITEM=#ONT(streetwear)]': {
                '#GET_FAV_CLOTHING`I see you over there with that model off duty style. Pop off queen.`': 'get_not_fav_clothing_transition'
            },
            '[$USER_FAV_CLOTHING_ITEM=#ONT(classic)]': {
                '#GET_FAV_CLOTHING`So you like to dress like you\'re going to work all the time? Sorry that might have been a little mean.\n `': 'get_not_fav_clothing_transition'
            },
            '[$USER_FAV_CLOTHING_ITEM=#ONT(casual)]': {
                '#GET_FAV_CLOTHING`Fair answer. I spend most of my time in my Aritzia sweat suits.\n `': 'get_not_fav_clothing_transition'
            },
            '[$USER_FAV_CLOTHING_ITEM=#ONT(ethnic)]': {
                '#GET_FAV_CLOTHING`That\'s cool. I don\'t have one of those!\n `': 'get_not_fav_clothing_transition'
            },
            'error': {
                '`Sorry, I don\'t understand. Do you mind answering the question again?`': 'get_fav_clothing_transition'
            }
        }
    }

    choice_get_fav_clothing_transition = {
        '`Do you have any more clothing items you\'d like to add?`': {
            '{yes, absolutely, affirmative, certainly, "of course", sure, yup, yeah, "uh-huh", roger, aye, okay, agreed, indeed, right, positively, "you bet", correct, definitely, "absolutely right", indubitably}': 'get_fav_clothing_transition',
            '{no, nope, “nuh-uh”, negative, “not at all”, “no way”, “absolutely not”, never, “not really”, “i\’m afraid not”, “sorry, no”, “no chance”, “i don\'t think so”, “not a chance”, “unlikely”, “definitely not”, “no thanks”, nay, refusal, rejection, veto}': 'get_not_fav_clothing_transition',
            'error': {
                '`Sorry, I don\'t understand. Do you mind answering the question again?`': 'choice_get_fav_clothing_transition'
            }
        }
    }

    # -- get user's not preferred clothing items
    get_not_fav_clothing_transition = {
        'state': 'get_not_fav_clothing_transition',
        '`What about a clothing item that you would never wear?`': {
            '[$USER_NOT_FAV_CLOTHING_ITEM=#ONT(sporty)]': {
                '#GET_NOT_FAV_CLOTHING`I feel you. I only wear athleisure when I\'m too lazy to put together an outfit.\n `': 'choice_recommendation_transition'
            },
            '[$USER_NOT_FAV_CLOTHING_ITEM=#ONT(bohemian)]': {
                '#GET_NOT_FAV_CLOTHING`I feel you. Fringed, flowy, and frayed is dfinitely not for everyone.\n `': 'choice_recommendation_transition'
            },
            '[$USER_NOT_FAV_CLOTHING_ITEM=#ONT(grunge)]': {
                '#GET_NOT_FAV_CLOTHING`I feel you. I\'m not quite into the whole distressing everything vibe.\n `': 'choice_recommendation_transition'
            },
            '[$USER_NOT_FAV_CLOTHING_ITEM=#ONT(preppy)]': {
                '#GET_NOT_FAV_CLOTHING`I feel you. Whenever I put on a polo, I don\'t quite feel like myself.\n `': 'choice_recommendation_transition'
            },
            '[$USER_NOT_FAV_CLOTHING_ITEM=#ONT(punk)]': {
                '#GET_NOT_FAV_CLOTHING`I feel you. Fish nets, studded belts, and chokers aren\'t really my cup of tea either.\n `': 'choice_recommendation_transition'
            },
            '[$USER_NOT_FAV_CLOTHING_ITEM=#ONT(streetwear)]': {
                '#GET_NOT_FAV_CLOTHING`I feel you, but honestly you\'re missing out. I\'m an oversized, cargo, and low rise fanatic.\n `': 'choice_recommendation_transition'
            },
            '[$USER_NOT_FAV_CLOTHING_ITEM=#ONT(classic)]': {
                '#GET_NOT_FAV_CLOTHING`I feel you. The only time you\'ll catch me in clothes that look like I\'m going to work when I\'m actually going to work. Or if it\'s Chanel tweed ofc.\n `': 'choice_recommendation_transition'
            },
            '[$USER_NOT_FAV_CLOTHING_ITEM=#ONT(casual)]': {
                '#GET_NOT_FAV_CLOTHING`I feel you. I am quite the over dresser myself. You\'re way better overdressed than under in my humble opinion.\n `': 'choice_recommendation_transition'
            },
            '[$USER_NOT_FAV_CLOTHING_ITEM=#ONT(ethnic)]': {
                '#GET_NOT_FAV_CLOTHING`I feel you. I don\'t wear too much of that either.\n `': 'choice_recommendation_transition'
            },
            'error': {
                '`Sorry, I don\'t understand`': 'get_not_fav_clothing_transition'
            }
        }
    }

    # -- ask if the user would like to be recommended an outfit
    # or help getting styled with an outfit they've already picked out
    choice_recommendation_transition = {
        'state': 'choice_recommendation_transition',
        '`Alright, now that I\'ve collected all this information about you.\n '
        'Would you like me to recommend you an outfit? Or do you need styling advice for an outfit your currently wearing?`': {
            '{<recommend>, <outfit>}': {
                '`Alright! I can recommend you an outfit.\n `#REC_OUTFIT`What do you think?`': {
                    # get the user's feedback about Becca's first recommendation
                    'state': 'return_to_feedback_choice_rec_transition',
                    '#GET_FEEDBACK': {
                        # if the user's feedback is considered postitve
                        '#IF($USER_SENTIMENT=positive)`I\'m happy you like my recommendation! \U0001F44F`': 'end',
                        # if the user's feedback is considered neutral
                        '#IF($USER_SENTIMENT=neutral)`I\'m not sure if my recommendation is something your\'re interested in, \U0001F937 but I\'m glad to hear you don\'t completely hate it!.\n '
                        'Would you like me to recommend you another outfit?`': {
                            '{yes, sure}': {
                                '`Okay, I can recommend you another outfit!`#REC_OUTFIT_AF_FEEDBACK`What do you think?`': 'return_to_feedback_choice_rec_transition'
                            },
                            'no': {
                                '`Alright, I won\'t give you any more recommendations.`': 'end'
                            },
                            'error': {
                                '`Sorry, I don\'t understand.`': 'end'
                            }
                        },
                        # if the user's feedback is considered negative
                        '#IF($USER_SENTIMENT=negative)`I\'m sorry you don\'t my recommendation. \U0001F61E Would you like me to recommend you another outfit?`': {
                            'yes': {
                                '`Okay, I can recommend you another outfit!`#REC_OUTFIT_AF_FEEDBACK`What do you think?`': 'return_to_feedback_choice_rec_transition'
                            },
                            '{no, nah, nope, "I\'m good", "I\'m ok"}': {
                                '`Alright, I won\'t give you any more recommendations.`': 'end'
                            },
                            'error': {
                                '`Sorry, I don\'t understand.`': 'end'
                            }
                        }
                    }
                }
            },
            '[styling, advice]': {
                '`Alright, I can help you style your current outfit!\n '
                'Before I can do that though, I gotta know what you\'re wearing!\n So, `': 'get_current_top_transition'
            }
        }
    }

    # -- get user's current outfit #1
    # -- get the top the user is wearing
    get_current_top_transition = {
        'state': 'get_current_top_transition',
        '`what top are you currently wearing? Otherwise, say skip.`': {
            '[$USER_CURR_ITEM=#ONT(sporty)]': {
                '#GET_CURR_OUTFIT`Got it, nice! I wore a soccer jersey with a pleated skirt yesterday to the Atlanta United game. Let\'s move on to the next item of clothing.\n `': 'get_current_bottoms_transition'
            },
            '[$USER_CURR_ITEM=#ONT(bohemian)]': {
                '#GET_CURR_OUTFIT`Got it, nice! I\'m obsessed with my sheer bell sleeve top from Free People. Let\'s move on to the next item of clothing.\n `': 'get_current_bottoms_transition'
            },
            '[$USER_CURR_ITEM=#ONT(grunge)]': {
                '#GET_CURR_OUTFIT`Got it, nice! I thrifted the coolest black tank with rips originally from Jaded London top the other day. Let\'s move on to the next item of clothing.\n `': 'get_current_bottoms_transition'
            },
            '[$USER_CURR_ITEM=#ONT(preppy)]': {
                '#GET_CURR_OUTFIT`Got it, nice! I have a cropped collared t-shirt my Aunt gave that I\'ve been meaning to style. Let\'s move on to the next item of clothing.\n `': 'get_current_bottoms_transition'
            },
            '[$USER_CURR_ITEM=#ONT(punk)]': {
                '#GET_CURR_OUTFIT`Got it, nice! The other day I wore my Rolling Stones band t-shirt with jean shorts and sneakers and it was a vibe! Let\'s move on to the next item of clothing.\n `': 'get_current_bottoms_transition'
            },
            '[$USER_CURR_ITEM=#ONT(streetwear)]': {
                '#GET_CURR_OUTFIT`Got it, nice! I\'ve been on the hunt for a denim vest so I can have my Canadian Tuxedo moment. Let\'s move on to the next item of clothing.\n `': 'get_current_bottoms_transition'
            },
            '[$USER_CURR_ITEM=#ONT(classic)]': {
                '#GET_CURR_OUTFIT`Got it, nice! Let\'s move on to the next item of clothing.\n `': 'get_current_bottoms_transition'
            },
            '[$USER_CURR_ITEM=#ONT(casual)]': {
                '#GET_CURR_OUTFIT`Got it, nice! I wore an oversized blazer to work last week and felt super cool lol. Let\'s move on to the next item of clothing.\n `': 'get_current_bottoms_transition'
            },
            '[$USER_CURR_ITEM=#ONT(ethnic)]': {
                '#GET_CURR_OUTFIT`Got it, nice! I\'m sure it\'s a beautiful garment. Let\'s move on to the next item of clothing.\n `': 'get_current_bottoms_transition'
            },
            # if the user is wearing nothing, or something similar to nothing, return don't do anythgin in the current outfit dict
            '<skip>': {
                '$USER_CURR_ITEM=""#GET_CURR_OUTFIT`Okay, so you\'re not wearing that item. I can work with that.\n `': 'get_current_bottoms_transition'
            },
            'error': {
                '`I\'m not sure I understand.`': 'get_current_top_transition'
            }
        }
    }

    # -- get the user's current outfit #2
    # -- get the bottom the user is wearing
    get_current_bottoms_transition = {
        'state': 'get_current_bottoms_transition',
        '`What bottoms are you currently wearing? Otherwise, say skip.`': {
            '[$USER_CURR_ITEM=#ONT(sporty)]': {
                '#GET_CURR_OUTFIT`Understood. I\'m a tennis skirt girlie. I wore one yesterday to workout. Moving on to the next item.\n `': 'get_current_coat_transition'
            },
            '[$USER_CURR_ITEM=#ONT(bohemian)]': {
                '#GET_CURR_OUTFIT`Understood. I wore the coolest plaid flared pants from Free People to a 70s party last weekend. Moving on to the next item.\n `': 'get_current_coat_transition'
            },
            '[$USER_CURR_ITEM=#ONT(grunge)]': {
                '#GET_CURR_OUTFIT`Understood. I\'ve been obsessed with the Melina leather pants from Aritzia lately. Moving on to the next item.\n `': 'get_current_coat_transition'
            },
            '[$USER_CURR_ITEM=#ONT(preppy)]': {
                '#GET_CURR_OUTFIT`Understood. I wear my black pleated skirt all the time. I\'m thinking about investing in another color! Moving on to the next item.\n `': 'get_current_coat_transition'
            },
            '[$USER_CURR_ITEM=#ONT(punk)]': {
                '#GET_CURR_OUTFIT`Understood. My black leather is skirt is my ride or die for going out. Moving on to the next item.\n `': 'get_current_coat_transition'
            },
            '[$USER_CURR_ITEM=#ONT(streetwear)]': {
                '#GET_CURR_OUTFIT`Understood. I love that for you. I will never stop wearing mom jeans, idc what people say. Moving on to the next item.\n `': 'get_current_coat_transition'
            },
            '[$USER_CURR_ITEM=#ONT(classic)]': {
                '#GET_CURR_OUTFIT`Understood. I have this royal blue silk skirt that I\'m so excited to wear this spring. Moving on to the next item.\n `': 'get_current_coat_transition'
            },
            '[$USER_CURR_ITEM=#ONT(casual)]': {
                '#GET_CURR_OUTFIT`Understood. I\'m literally wearing sweatpants right now lol. Moving on to the next item.\n `': 'get_current_coat_transition'
            },
            '[$USER_CURR_ITEM=#ONT(ethnic)]': {
                '#GET_CURR_OUTFIT`Understood. Ralph Lauren\'s 2009 Harem pants were iconic. Moving on to the next item.\n `': 'get_current_coat_transition'
            },
            # if the user is wearing nothing, or something similar to nothing, return don't do anythgin in the current outfit dict
            '<skip>': {
                '$USER_CURR_ITEM=""#GET_CURR_OUTFIT`Okay, so you\'re not wearing that item. I can work with that.\n `': 'get_current_coat_transition'
            },
            'error': {
                '`I\'m not sure I understand.`': 'get_current_bottoms_transition'
            }
        }
    }

    # -- get the user's current outfit #3
    # -- get the outerwear the user is wearing
    get_current_coat_transition = {
        'state': 'get_current_coat_transition',
        '`What coat or outerwear are you currently wearing? Otherwise, say skip.`': {
            '[$USER_CURR_ITEM=#ONT(sporty)]': {
                '#GET_CURR_OUTFIT`Cool! I literally live in my Nike track jacket. It\'s perfectly oversized and so comfy. And now...\n `': 'get_current_shoes_transition'
            },
            '[$USER_CURR_ITEM=#ONT(bohemian)]': {
                '#GET_CURR_OUTFIT`Cool! I\'ve actually been meaning to get my denim jacket embroidered with little flowers. And now...\n `': 'get_current_shoes_transition'
            },
            '[$USER_CURR_ITEM=#ONT(grunge)]': {
                '#GET_CURR_OUTFIT`Cool! I\'m a strong believer that everyone needs a good leather jacket in their closet. And now...\n `': 'get_current_shoes_transition'
            },
            '[$USER_CURR_ITEM=#ONT(preppy)]': {
                '#GET_CURR_OUTFIT`Cool! Maybe one day I\'ll be able to buy myself the iconic Burberry trench. Wow, that would make my year. And now...\n `': 'get_current_shoes_transition'
            },
            '[$USER_CURR_ITEM=#ONT(punk)]': {
                '#GET_CURR_OUTFIT`Cool! I LOVE my Wilsons biker jacket from Ebay. It has an orange stripe down the sleeve and it so unique. And now...\n `': 'get_current_shoes_transition'
            },
            '[$USER_CURR_ITEM=#ONT(streetwear)]': {
                '#GET_CURR_OUTFIT`Cool! I thrifted the sickest patchwork jacket from Depop the other day. I\'m so excited to wear it. And now...\n `': 'get_current_shoes_transition'
            },
            '[$USER_CURR_ITEM=#ONT(classic)]': {
                '#GET_CURR_OUTFIT`Cool! I love a classic peacoat. I\'ve been eyeing one from Ralph Lauren forever. And now...\n `': 'get_current_shoes_transition'
            },
            '[$USER_CURR_ITEM=#ONT(casual)]': {
                '#GET_CURR_OUTFIT`Cool! I feel like baseball jackets are also super trendy right now. I need to hop on that trend. And now...\n `': 'get_current_shoes_transition'
            },
            '[$USER_CURR_ITEM=#ONT(ethnic)]': {
                '#GET_CURR_OUTFIT`Cool! I saw the most beautiful embroidered tunic the other day. And now...\n `': 'get_current_shoes_transition'
            },
            # if the user is wearing nothing, or something similar to nothing, return don't do anythgin in the current outfit dict
            '<skip>': {
                '$USER_CURR_ITEM=""#GET_CURR_OUTFIT`Okay, so you\'re not wearing that item. I can work with that.\n `': 'get_current_shoes_transition'
            },
            'error': {
                '`I\'m not sure I understand.`': 'get_current_coat_transition'
            }
        }
    }

    # -- get the user's current outfit #4
    # -- get the shoes the user is wearing
    get_current_shoes_transition = {
        'state': 'get_current_shoes_transition',
        '`What shoes are you currently wearing? Otherwise, say skip.`': {
            '[$USER_CURR_ITEM=#ONT(sporty)]': {
                '#GET_CURR_OUTFIT`Great. I just invested in a pair of Hokas and they literally make it feel like I\'m running on clouds. Also, one last thing...\n `': 'get_current_accessory_transition'
            },
            '[$USER_CURR_ITEM=#ONT(bohemian)]': {
                '#GET_CURR_OUTFIT`Great. I recently bought a pair of fringed sandals from Target for summer I\'m super excited to wear them. Also, one last thing...\n `': 'get_current_accessory_transition'
            },
            '[$USER_CURR_ITEM=#ONT(grunge)]': {
                '#GET_CURR_OUTFIT`Great. I\'ve been wanting to style my combat boots. I got them awile ago and haven\'t worn them for a long time. Also, one last thing...\n `': 'get_current_accessory_transition'
            },
            '[$USER_CURR_ITEM=#ONT(preppy)]': {
                '#GET_CURR_OUTFIT`Great. I\'ve really been wanting a pair of Golden Goose. I\'ve seen a lot of people wearing them. Also, one last thing...\n `': 'get_current_accessory_transition'
            },
            '[$USER_CURR_ITEM=#ONT(punk)]': {
                '#GET_CURR_OUTFIT`Great. I love my moto boots from Frye. I really need to wear those more. Also, one last thing...\n `': 'get_current_accessory_transition'
            },
            '[$USER_CURR_ITEM=#ONT(streetwear)]': {
                '#GET_CURR_OUTFIT`Great. I\'ve been wanting a pair of black and white Nike high tops. Also, one last thing...\n `': 'get_current_accessory_transition'
            },
            '[$USER_CURR_ITEM=#ONT(classic)]': {
                '#GET_CURR_OUTFIT`Great. I love how versatile loafers are. I\ve been able to style them in so many different ways. Also, one last thing...\n `': 'get_current_accessory_transition'
            },
            '[$USER_CURR_ITEM=#ONT(casual)]': {
                '#GET_CURR_OUTFIT`Great. I love my white high top converse. I wore them literally every day last summer. Also, one last thing...\n `': 'get_current_accessory_transition'
            },
            '[$USER_CURR_ITEM=#ONT(ethnic)]': {
                '#GET_CURR_OUTFIT`Great. That\'s so cool. I\'d love to learn more about the different types of shoes worn around the world. Also, one last thing...\n `': 'get_current_accessory_transition'
            },
            # if the user is wearing nothing, or something similar to nothing, return don't do anythgin in the current outfit dict
            '<skip>': {
                '$USER_CURR_ITEM=""#GET_CURR_OUTFIT`Okay, so you\'re not wearing that item. I can work with that.\n `': 'get_current_accessory_transition'
            },
            'error': {
                '`I\'m not sure I understand.`': 'get_current_shoes_transition'
            }
        }
    }

    # -- get the user's current outfit #5
    # -- get any accessories the user is currently wearing
    get_current_accessory_transition = {
        'state': 'get_current_accessory_transition',
        '`What accessory are you currently wearing? Otherwise, say skip.`': {
            '[$USER_CURR_ACCSRY=#ONT(sporty)]': {
                '#GET_CURR_OUTFIT`Awesome, thanks! I like wearing a baseball cap when I don\'t want to talk to people in public lol.\n `': 'choice_acessory_transition'
            },
            '[$USER_CURR_ACCSRY=#ONT(bohemian)]': {
                '#GET_CURR_OUTFIT`Awesome, thanks! I\'ve been looking for a pair of oversized sunnies for this summer.\n `': 'choice_acessory_transition'
            },
            '[$USER_CURR_ACCSRY=#ONT(grunge)]': {
                '#GET_CURR_OUTFIT`Awesome, thanks! Chokers are really trending these days. I guess I need to hop on that trend.\n `': 'choice_acessory_transition'
            },
            '[$USER_CURR_ACCSRY=#ONT(preppy)]': {
                '#GET_CURR_OUTFIT`Awesome, thanks! I recently bought the cutest tote bag at a night market in Costa Rica. I\'m obsessed with it.\n `': 'choice_acessory_transition'
            },
            '[$USER_CURR_ACCSRY=#ONT(punk)]': {
                '#GET_CURR_OUTFIT`Awesome, thanks! My mom sent me an adorable picture of her in a studded belt that she recently bought.\n `': 'choice_acessory_transition'
            },
            '[$USER_CURR_ACCSRY=#ONT(streetwear)]': {
                '#GET_CURR_OUTFIT`Awesome, thanks! So apparently people are wearing ski glasses for fun these days? I definitely need to look into that.\n `': 'choice_acessory_transition'
            },
            '[$USER_CURR_ACCSRY=#ONT(classic)]': {
                '#GET_CURR_OUTFIT`Awesome, thanks! People have been styling silk scarves all types of ways on TikTok. Who knew a scarf could function as ten different tops?\n `': 'choice_acessory_transition'
            },
            '[$USER_CURR_ACCSRY=#ONT(casual)]': {
                '#GET_CURR_OUTFIT`Awesome, thanks! I\'ve been meaning to get myself a straw hat for this summer. Any recs would be greatly appreciated!\n `': 'choice_acessory_transition'
            },
            '[$USER_CURR_ACCSRY=#ONT(ethnic)]': {
                '#GET_CURR_OUTFIT`Awesome, thanks! I saw someone wearing the most beautiful traditional jewelry the other day. I\'m dying to know where it was from.\n `': 'choice_acessory_transition'
            },

            # if the user is wearing nothing, or something similar to nothing, return don't do anythgin in the current outfit dict
            '<skip>': {
                '$USER_CURR_ITEM=""#GET_CURR_OUTFIT`Okay, so you\'re not wearing that item. I can work with that.\n `': 'choice_acessory_transition'
            },
            'error': {
                '`I\'m not sure I understand.`': 'get_current_accessory_transition'
            }
        }
    }

    # -- asks the user if they have any more accessories they'd like to list
    choice_acessory_transition = {
        'state': 'choice_acessory_transition',
        '`Are you wearing any more accessories?`': {
            '{yes, yeah, yup, ye, yea, indeed, , yessir, [i am]}': 'get_current_accessory_transition',
            '{no, nah, nope, [i am not], [i\'m not]}': 'return_current_outfit_advice_transition'
        }
    }

    # -- given the user's current oufit, recommend a clothing item that would go with it
    return_outfit_recommendation_transition = {
        'state': 'return_outfit_recommendation_transition',
        '`Alright, given the information I\'ve recived about what you\'re currently wearing,`#REC_CLOTHING_ITEM`What do you think?`': {
            'state': 'return_to_feedback_outfit_rec',
            '#GET_FEEDBACK': {
                # if the user's feedback is considered positive
                '#IF($USER_SENTIMENT=positive)`I\'m happy you like my recommendation! \U0001F44F`': 'end',
                # if the user's feedback is considered neutral
                '#IF($USER_SENTIMENT=neutral)`I\'m not sure if my recommendation is something your\'re interested in, \U0001F937 but I\'m glad to hear you don\'t completely hate it!.\n '
                'Would you like me to recommend you another outfit?`': {
                    '{yes, yeah, yup, ye, yea, indeed, sure, ok, okay, fine}': {
                        '`Okay, I can recommend you another outfit!`#REC_CLOTHING_ITEM_AF_FEEDBACK`What do you think?`': 'return_to_feedback_outfit_rec'
                    },
                    '{no, nah, nope, [i\'m good], [not right now], [absolutely not], [i\'m done], [i\'m finished]}': {
                        '`Alright, I won\'t give you any more recommendations.`': 'end'
                    },
                    'error': {
                        '`Sorry, I don\'t understand.`': 'end'
                    }
                },
                # if the user's feedback is considered negative
                '#IF($USER_SENTIMENT=negative)`I\'m sorry you don\'t my recommendation. \U0001F616 Would you like me to recommend you another outfit?`': {
                    '{yes, yeah, yup, ye, yea, indeed, sure, ok, okay, fine}': {
                        '`Okay, I can recommend you another outfit!`#REC_CLOTHING_ITEM_AF_FEEDBACK`What do you think?`': 'return_to_feedback_outfit_rec'
                    },
                    '{no, nah, nope, [i\'m good], [not right now], [absolutely not], [i\'m done], [i\'m finished]}': {
                        '`Alright, I won\'t give you any more recommendations.`': 'end'
                    },
                    'error': {
                        '`Sorry, I don\'t understand.`': 'end'
                    }
                }
            }
        }
    }

    exit_transition = {
        'state': 'exit_transition',
        '`Well that\'s all I really have for you.\n '
        'I\'d really apprecate if if you would take a quick survey on my performance. Would you be willing to do so?`': {
            'yes': {
                '`Okay, great! The link to the survey is here: "https://forms.gle/jJGy46m3PSQdZwiC8" I hope you have a wonderful and stylish day!`': 'end'
            },
            'no': {
                '`That\'s fine too. I hope you have a wonderful and stylish day!`': 'end'
            }
        }
    }

    # macro references ============================================
    macros = {
        'GET_NAME': MacroGetName(),
        'GET_AGE': MacroSaveAge(),
        'RETURN_AGE_RESPONSE': MacroReturnAgeResponse(),
        'GET_OCCUPATION': MacroSaveOccupation(),
        'RETURN_OCC_RESPONSE': MacroOccupationResponse(),
        'GET_HOBBY': MacroSaveHobby(),
        'GET_FAV_COLOR': MacroSaveFavoriteColor(),
        'GET_NOT_FAV_COLOR': MacroSaveNotFavoriteColor(),
        'GET_STYLE': MacroSaveStyle(),
        'GET_FAV_CLOTHING': MacroSaveFavoriteClothing(),
        'GET_NOT_FAV_CLOTHING': MacroSaveNotFavoriteClothing(),
        'GET_CURR_OUTFIT': MacroSaveOutfit(),
        # macros for talking about the movie ============================================
        'GET_WATCH_STATUS': MacroReturnWatchStatus(),
        # macros for recommending clothes ============================================
        'REC_OUTFIT': MacroRecommendOutfit(),
        'GET_FEEDBACK': MacroReturnFeedbackSentiment(),
        'REC_OUTFIT_AF_FEEDBACK': MacroRecommendOutfitAfterFeedback(),
        'REC_CLOTHING_ITEM': MacroRecommentClothingItem(),
        'REC_CLOTHING_ITEM_AF_FEEDBACK': MacroRecommendClothingItemAfterFeedback(),

    }

    # ============================================
    df = DialogueFlow('start', end_state='end')

    df.knowledge_base().load_json_file('./resources/occupation_ontology.json')
    df.knowledge_base().load_json_file('./resources/hobbies_ontology.json')
    df.knowledge_base().load_json_file('./resources/color_names_ontology.json')
    df.knowledge_base().load_json_file('./resources/styles_ontology.json')
    df.knowledge_base().load_json_file('./resources/clothing_items_ontology.json')

    df.load_transitions(introduction_transition)

    df.load_transitions(return_user_transition)
    df.load_transitions(new_user_transition)

    # df.load_transitions(choice_transition)
    df.load_transitions(babel_transition)

    df.load_transitions(clothing_transition)

    # get the user's age
    df.load_transitions(get_age_transition)

    # get the users occupation
    df.load_transitions(get_occupation_transition)

    # get the user's hobby (3x
    df.load_transitions(get_hobby_transition_one)
    df.load_transitions(get_hobby_transition_two)
    df.load_transitions(get_hobby_transition_three)

    # get the user's favourite colours (2x)
    df.load_transitions(get_fav_color_transition_one)
    df.load_transitions(get_fav_color_transition_two)

    # get the user's not favourite colour
    df.load_transitions(get_not_fav_color_transition)

    # get the user's preffered styles (2x)
    df.load_transitions(get_style_transition_one)
    df.load_transitions(get_style_transition_two)

    # get the user's favourite clothing item
    df.load_transitions(get_fav_clothing_transition)

    # get the user's not favourite clothing item
    df.load_transitions(get_not_fav_clothing_transition)

    df.load_transitions(choice_get_fav_clothing_transition)

    # get the user's current outfit
    df.load_transitions(get_current_top_transition)
    df.load_transitions(get_current_bottoms_transition)
    df.load_transitions(get_current_coat_transition)
    df.load_transitions(get_current_shoes_transition)
    df.load_transitions(get_current_accessory_transition)

    # ask if the user is wearing any more accessories
    # if yes, double back to get_current_accessory_transition
    # if no, move on to next transition
    df.load_transitions(choice_acessory_transition)

    # ask if the user whats to get recommended a whole outfit
    # or if they want styling advice for their current outfit
    # if yes whole outfit, return whole outfit recommendation
    df.load_transitions(choice_recommendation_transition)

    # return, recommednation for user's current outift
    df.load_transitions(return_outfit_recommendation_transition)

    # exting conversation -- directs user to google form
    df.load_transitions(exit_transition)

    df.add_macros(macros)

    return df


# run dialogue ======================================================
if __name__ == '__main__':
    # save(main_dialogue(), 'users-pickle.pkl')
    load(main_dialogue(), 'users-pickle.pkl')
