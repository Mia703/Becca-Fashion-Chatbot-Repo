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
# python files ============================================
# TODO: api_file.py is ignored by github for privacy reasons
from api_file import API_KEY
# import babble_macros
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
openai.api_key = API_KEY

# saves the user's feedback from recommendation
user_feedback = ''

# saves the last recommendation to the user
last_recommendation = ''

# macros ============================================

# saves and returns the user's name
class MacroGetName(Macro):
	def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
		global users_dictionary
		global current_user

		r = re.compile(r"(mr|mrs|ms|dr)?(?:^|\s)([a-z']+)(?:\s([a-z']+))?")
		m = r.search(ngrams.text())
		if m is None: return False

		title, firstname, lastname = None, None, None

		if m.group(1):
			title = m.group(1)
			if m.group(3):
				firstname = m.group(2)
				lastname = m.group(3)
			else:
				firstname = m.group()
				lastname = m.group(2)
		else:
			firstname = m.group(2)
			lastname = m.group(3)

		# save the current user
		current_user = firstname

		vars['TITLE'] = title
		vars['FIRSTNAME'] = firstname.capitalize()
		vars['LASTNAME'] = lastname

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
		print(users_dictionary)

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
		user_nested_list.append(user_hobby)

		print(users_dictionary)


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
		user_nested_list.append(color_hex)

		print(users_dictionary)


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
		user_nested_list.append(color_hex)

		print(users_dictionary)


# save the user's favourite styles
class MacroSaveStyle(Macro):
	def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
		global users_dictionary
		global current_user
		global styles_df

		# get the user's style or the clothing item associated with the style
		user_style_item = str(vars['USER_STYLE'])

		# search the dataframe for the item
		# -- returns a dataframe with the row of the colour
		df_results = styles_df.loc[styles_df['Clothing'] == user_style_item]
		# print(df_results)

		# get the index of the row
		style_index = list(df_results.index.values)[0]

		# save the style name
		style_name = df_results['Style'][style_index]

		# access the user's dictionary
		user_nested_dictionary = users_dictionary[current_user]

		# access the user's style list
		user_nested_list = user_nested_dictionary['style_list']

		# append the style name to the list
		user_nested_list.append(style_name)

		print(users_dictionary)


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
		user_nested_list.append(user_fav_item)

		print(users_dictionary)


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
		user_nested_list.append(user_not_fav_item)

		print(users_dictionary)


# saves the user's current outfit
class MacroSaveOutfit(Macro):
	def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
		global users_dictionary
		global current_user
		global styles_df

		# get the user’s current clothing item
		user_item = str(vars['USER_CURR_ITEM'])
		print('user item: ' + user_item)

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
		print('current outfit dictionary size: ' + str(dict_index))

		# add the clothing item, category, and style to the user's current outfit dictinoary
		user_nested_current_outfit_dictionary[dict_index] = dict(
			clothing_item=str(clothing_item),
			clothing_category=str(clothing_category),
			clothing_style=str(clothing_style)
		)

		print(user_nested_current_outfit_dictionary)


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

		# TODO: should there be a check here to make sure the list isn't empty
		# an empty list causes an error
		# randomly select an item from each list
		random_hobby_index = random.randint(0, len(user_hobbies_list)-1)
		random_fav_color_index = random.randint(0, len(user_fav_colors_list)-1)
		random_not_fav_color_index = random.randint(0, len(user_not_fav_colors_list)-1)
		random_style_index = random.randint(0, len(user_style_list)-1)
		random_fav_clothes_index = random.randint(0, len(user_fav_clothes_list)-1)
		random_not_fav_clothes_index = random.randint(0, len(user_not_fav_clothes_list)-1)

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

		return 'I would recommend ' + outfit_recommendation.lower()


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
class MacroRecommendOutfitAfterFeedback (Macro):
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

		# TODO: should there be a check here to make sure the list isn't empty
		# an empty list causes an error
		# randomly select an item from each list
		random_hobby_index = random.randint(0, len(user_hobbies_list)-1)
		random_fav_color_index = random.randint(0, len(user_fav_colors_list)-1)
		random_not_fav_color_index = random.randint(0, len(user_not_fav_colors_list)-1)
		random_style_index = random.randint(0, len(user_style_list)-1)
		random_fav_clothes_index = random.randint(0, len(user_fav_clothes_list)-1)
		random_not_fav_clothes_index = random.randint(0, len(user_not_fav_clothes_list)-1)

		# call function
		outfit_recommendation = recommendOutfitAfterFeedback(
			hobby=user_hobbies_list[random_hobby_index],
			fav_color=user_fav_colors_list[random_fav_color_index],
			not_fav_color=user_not_fav_colors_list[random_not_fav_color_index],
			user_style=user_style_list[random_style_index],
			fav_item=user_fav_clothes_list[random_fav_clothes_index],
			not_fav_item=user_not_fav_clothes_list[random_not_fav_clothes_index],
			feedback=user_feedback,
			sentiment= vars['USER_SENTIMENT']
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
		

		# TODO: should there be a check here to make sure the list isn't empty
		# an empty list causes an error
		# randomly select an item from each list
		random_hobby_index = random.randint(0, len(user_hobbies_list)-1)
		random_fav_color_index = random.randint(0, len(user_fav_colors_list)-1)
		random_not_fav_color_index = random.randint(0, len(user_not_fav_colors_list)-1)
		random_style_index = random.randint(0, len(user_style_list)-1)
		random_fav_clothes_index = random.randint(0, len(user_fav_clothes_list)-1)
		random_not_fav_clothes_index = random.randint(0, len(user_not_fav_clothes_list)-1)

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

		# TODO: remove the period?
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

		# TODO: should there be a check here to make sure the list isn't empty
		# an empty list causes an error
		# randomly select an item from each list
		random_hobby_index = random.randint(0, len(user_hobbies_list)-1)
		random_fav_color_index = random.randint(0, len(user_fav_colors_list)-1)
		random_not_fav_color_index = random.randint(0, len(user_not_fav_colors_list)-1)
		random_style_index = random.randint(0, len(user_style_list)-1)
		random_fav_clothes_index = random.randint(0, len(user_fav_clothes_list)-1)
		random_not_fav_clothes_index = random.randint(0, len(user_not_fav_clothes_list)-1)

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
			sentiment= vars['USER_SENTIMENT'],
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


# checks if the user is already in the user_dictionary
# if not -- new user -- creates a empty dictionary with the users name
# if is -- return user -- does nothing
def createUserCheck():
	global users_dictionary
	global current_user

	print("The current user is " + current_user)

	# if the user is not already in the dictionary
	# create a empty dictionary with the user's name
	if users_dictionary.get(current_user) is None:
		print("Creating a new user " + current_user)

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
		
		print(users_dictionary)
		return 'no'

	# else, the user is already in the dictionary -- returning user
	else:
		print("A returning user: " + current_user)
		return 'yes'


# recommens an outfit to the user
def recommendOutfit(hobby, fav_color, not_fav_color, user_style, fav_item, not_fav_item):
	prompt = 'Recommend an outfit for someone who likes ' + hobby + ', the color ' + fav_color + ', hates the color ' + not_fav_color + ', dresses in the ' + user_style + ' style, likes to wear ' + fav_item + ', and doesn\'t like to wear ' + not_fav_item + '. Put your response in a sentence. Don\'t explain.'

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
def recommendOutfitAfterFeedback(hobby, fav_color, not_fav_color, user_style, fav_item, not_fav_item, feedback, sentiment):
	prompt = 'Recommend a real clothing item for someone who likes ' + hobby + ', the color ' + fav_color + ', hates the color ' + not_fav_color + ', dresses in the ' + user_style + ' style, likes to wear ' + fav_item + ', and does\'t like to wear ' + not_fav_item + '. Your last recommendation was: ' + last_recommendation + ' and that person gave the following ' + sentiment + ' feedback: ' + feedback + '. Put your response in a sentence. Don\'t explain.'

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
def recommendClothingItemAfterFeedback(hobby, fav_color, not_fav_color, user_style, fav_item, not_fav_item, outfit, feedback, sentiment):
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

# dialogue ============================================
def main_dialogue() -> DialogueFlow:
	introduction_transition = {
		'state': 'start',
		'`Hi, what\'s your name?`': {
			'#GET_NAME': {
				# they are a returning user
				# '#IF($RETURN_USER=yes)': 'return_user_transition',
				'#IF($RETURN_USER=yes)': 'return_current_outfit_advice_transition',
				# they are a new user
				'#IF($RETURN_USER=no)': 'new_user_transition'
			}
		}
	}
	
	return_user_transition = {
		'state': 'return_user_transition',
		'`Welcome back`$FIRSTNAME`! Would you like to talk about the movie \"Babble\", jump right in to recommending, or update your preferences?`': {
			'<babble>': {
				# TODO: change back when done with babble transition
				# '`Okay, we can talk about the movie \"Babble\"!`': 'babble_transition'
				'`Okay, we can talk about the movie \"Babble\"!`': 'end'
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


	new_user_transition = {
		'state': 'new_user_transition',
		'`Nice to meet you`$FIRSTNAME`. My name is Becca! '
		'I\'m your personal stylist bot created just for you.\n '
		'I\'m here to help you look good and feel good about yourself and your clothes.\n '
		'And just an F.Y.I the information you share with me will stay with me. \U0001F92B\n '
		'So, let\'s get started! Would you like to talk about the movie \"Babble\" or shall we talk about you and your clothes?`': {
			'<babble>': {
				# TODO: change back when done with babble transition
				# '`Okay, we can talk about the movie \"Babble\"!`': 'babble_transition'
				'`Okay, we can talk about the movie \"Babble\"!`': 'end'
			},
			# Let's talk about clothes
			'[{let, lets, wanna, want}, clothes]': {
				'`Okay, we can talk about clothes!\n`': 'clothing_transition'
			},
			'error': {
				'`Sorry, I don\'t understand.`': 'new_user_transition'
			}
		}
	}


	# let's talk about Babble
	babble_transition = {
		'state': 'babble_transition',
		'`Have you already watched the movie \"Babble\" or would you like to learn more about the film?`': {
			'#SET_WATCH_STATUS':{
				'state': 'user_rating',
				# the user has watched the film
				'#IF($WATCH_STATUS=yes)`Did you enjoy the movie? What did you like or dislike about the movie?`': {
					# the user's rating for the movie was positive
					'#IF($USER_RATING=positive) `Glad to hear you enjoyed the movie.\n '
					'What were your thoughts on some of the themes or messages in the movie?`': {
						# don't really care what the user says here
						'error': {
							'`Yeah. I felt that this movie\'s main theme was that cultural and language barriers '
							'can lead to misunderstandings that lead to severe consequeces.\n '
							'None of the characters in this movie have bad intentions; however, things quickly spiral out of control due to misunderstandings.\n '
							'For example, the character Yussef naively underestimates the range of the rifle given to Hasan and shot an American tourist.\n '
							'The Americans incorrectly label the incident as an act of terror due to the stereotype associated with Morocco.\n '
							'As a result, Yasujiro, who gave a rifle to Hasan as a gesture of appreciation, came under investigation in Japan.\n '
							'He was suspected of dealing in the black market.\n '
							'Lastly, Amelia was forced to take of the American couple\'s kids for longer than anticipated due to Susan getting shot.\n '
							'However, she must show up to her son\'s wedding. Out of a sense of duty, she brings the couple\'s children with her to Mexico,\n '
							'which ends up being an incredibly poor decision.\n '
							'Due to a lack of written consent, the border patrol became suspicious and places her under arrest, which leads to her deportation.\n '
							'As we can see here, a combination of poor decisions and misunderstandings blew things out of proportion in these storylines.\n '
							'Do you have any additional thoughts on the characters?`': {
								# don't really care about what the user says here
								'error': {
									'`Out of all the characters in this movie, I have the most sympathy for Amelia.\n '
									'She had the best intentions and treated the couple\'s children like her own.\n '
									'Due to a the poor decision of taking the children across the border, '
									'she competely ruined her life and was treated like a criminal.\n '
									'On the other hand, Yussef and his brother just ruins it for everyone else.\n '
									'It has been great talking about the movie with you. Would you like to go back and learn more about clothing?`': {
										'[{yes, of course, alright, ok}]': {
											'`Sounds good`': 'clothing_transition'
										},
										'[{no, I\'m good, I am good, don\'t, do not}]' :{
											'It was good talking with you': 'end'
										}
									}
								}
							}
						}
					},
					# the user's rating for the move was neutral
					'#IF($USER_RATING=neutral)`Understandable. '
					'Personally, I felt the movie is pretty good overall. '
					'Only thing is, the Japan plotline feels a bit forced into the whole plot. '
					'What are your thoughts on some of the themes or messages in the movie?`': {
						# don't really care what the user says here
						'error': {
							'`Yeah. I felt that this movie\'s main theme was that cultural and language barriers '
							'can lead to misunderstandings that lead to severe consequeces.\n '
							'None of the characters in this movie have bad intentions; however, things quickly spiral out of control due to misunderstandings.\n '
							'For example, the character Yussef naively underestimates the range of the rifle given to Hasan and shot an American tourist.\n '
							'The Americans incorrectly label the incident as an act of terror due to the stereotype associated with Morocco.\n '
							'As a result, Yasujiro, who gave a rifle to Hasan as a gesture of appreciation, came under investigation in Japan.\n '
							'He was suspected of dealing in the black market.\n '
							'Lastly, Amelia was forced to take of the American couple\'s kids for longer than anticipated due to Susan getting shot.\n '
							'However, she must show up to her son\'s wedding. Out of a sense of duty, she brings the couple\'s children with her to Mexico,\n '
							'which ends up being an incredibly poor decision.\n '
							'Due to a lack of written consent, the border patrol became suspicious and places her under arrest, which leads to her deportation.\n '
							'As we can see here, a combination of poor decisions and misunderstandings blew things out of proportion in these storylines.\n '
							'Do you have any additional thoughts on the characters?`': {
								# don't really care about what the user says here
								'error': {
									'`Out of all the characters in this movie, I have the most sympathy for Amelia.\n '
									'She had the best intentions and treated the couple\'s children like her own.\n '
									'Due to a the poor decision of taking the children across the border, '
									'she competely ruined her life and was treated like a criminal.\n '
									'On the other hand, Yussef and his brother just ruins it for everyone else.\n '
									'It has been great talking about the movie with you. Would you like to go back and learn more about clothing?`': {
										'[{yes, of course, alright, ok}]': {
											'`Sounds good`': 'clothing_transition'
										},
										'[{no, I\'m good, I am good, don\'t, do not}]' :{
											'It was good talking with you': 'end'
										}
									}
								}
							}
						}
					},
					# the user's rating for the move was negative
					'#IF($USER_RATING=negative) `I personally thought Babel is a decent movie. '
					'I don\'t know if it deserves such a harsh review.\n '
					'What are your thoughts on some of the themes or messages in the movie?`': {
						'error': {
							'`Yeah. I felt that this movie\'s main theme was that cultural and language barriers '
							'can lead to misunderstandings that lead to severe consequeces.\n '
							'None of the characters in this movie have bad intentions; however, things quickly spiral out of control due to misunderstandings.\n '
							'For example, the character Yussef naively underestimates the range of the rifle given to Hasan and shot an American tourist.\n '
							'The Americans incorrectly label the incident as an act of terror due to the stereotype associated with Morocco.\n '
							'As a result, Yasujiro, who gave a rifle to Hasan as a gesture of appreciation, came under investigation in Japan.\n '
							'He was suspected of dealing in the black market.\n '
							'Lastly, Amelia was forced to take of the American couple\'s kids for longer than anticipated due to Susan getting shot.\n '
							'However, she must show up to her son\'s wedding. Out of a sense of duty, she brings the couple\'s children with her to Mexico,\n '
							'which ends up being an incredibly poor decision.\n '
							'Due to a lack of written consent, the border patrol became suspicious and places her under arrest, which leads to her deportation.\n '
							'As we can see here, a combination of poor decisions and misunderstandings blew things out of proportion in these storylines.\n '
							'Do you have any additional thoughts on the characters?`': {
								# don't really care about what the user says here
								'error': {
									'`Out of all the characters in this movie, I have the most sympathy for Amelia.\n '
									'She had the best intentions and treated the couple\'s children like her own.\n '
									'Due to a the poor decision of taking the children across the border, '
									'she competely ruined her life and was treated like a criminal.\n '
									'On the other hand, Yussef and his brother just ruins it for everyone else.\n '
									'It has been great talking about the movie with you. Would you like to go back and learn more about clothing?`': {
										'[{yes, of course, alright, ok}]': {
											'`Sounds good`': 'clothing_transition'
										},
										'[{no, I\'m good, I am good, don\'t, do not}]' :{
											'It was good talking with you': 'end'
										}
									}
								}
							}
						}
					},
					'`Sorry, I was not able to understand you. Let\'s try this again.`': {
						'state': 'USER_RATING',
						'score': 0.1
					}
				},
				# the user has NOT watched the film
				'#IF($WATCH_STATUS=no) `Babel is a psychological drama.\n '
				'An unintentional shooting incident connects four groups of people from different countries:\n '
				'a Japanese father and his teen daughter, a Moroccan goatherd family, a Mexican nanny, and an American couple '
				'(Brad Pitt and Cate Blanchett).\n All of these characters run into problems due to barriers in communication '
				'due to factors such as cultural and lanuage differences.`': {
					# don't really care what the user says here
					'error': {
						'`I believe this is a movie worth watching. Would you like to go back and learn more about clothes?`': {
							'[{yes, of course, alright, ok}]': {
								'`Sounds good`': 'clothing_transition'
							},
							'[{no, I\'m good, I am good, don\'t, do not}]': {
								'It was good talking with you': 'end'
							}
						}
					}
				},
				'`Sorry, I was not able to understand you. Let\'s try this again.`': {
					'state': 'babble_transition',
					'score': 0.1
				}
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
				'`I don\'t know much about that field, but it sounds like you must have a lot of expertise!`': 'end'
			}
		}
	}


	# -- gets the user's hobby 1
	get_hobby_transition_one = {
		'state': 'get_hobby_transition_one',
		'`Ah, I see! Speaking of... what do you do when you\'re not working?`': {
			# get hobby #1
			# learning = things that someone would learn for fun
			'[$USER_HOBBY=#ONT(learning)]': {
				'#GET_HOBBY`Interesting! When I\'m not working I love to read syfy-romance books.\n `': 'get_hobby_transition_two'
			},
			# sports = a physical activity
			'[$USER_HOBBY=#ONT(sports)]': {
				'#GET_HOBBY`Interesting! When I\'m not working I love to read syfy-romance books.\n `': 'get_hobby_transition_two'
			},
			# games = card/board games and the like
			'[$USER_HOBBY=#ONT(games)]': {
				'#GET_HOBBY`Interesting! When I\'m not working I love to read syfy-romance books.\n `': 'get_hobby_transition_two'
			},
			# creative = creating something; an artistic hobby
			'[$USER_HOBBY=#ONT(creative)]': {
				'#GET_HOBBY`Interesting! When I\'m not working I love to read syfy-romance books.\n `': 'get_hobby_transition_two'
			},
			# collecting = anything a person could collect
			'[$USER_HOBBY=#ONT(collecting)]': {
				'#GET_HOBBY`Interesting! When I\'m not working I love to read syfy-romance books.\n `': 'get_hobby_transition_two'
			},
			# domestic = chores that are hobbies
			'[$USER_HOBBY=#ONT(domestic)]': {
				'#GET_HOBBY`Interesting! When I\'m not working I love to read syfy-romance books.\n `': 'get_hobby_transition_two'
			},
			# making = making an object; tinkering
			'[$USER_HOBBY=#ONT(making)]': {
				'#GET_HOBBY`Interesting! When I\'m not working I love to read syfy-romance books.\n `': 'get_hobby_transition_two'
			},
			# outdoor = hobbies that happen outdoors; that aren't sports
			'[$USER_HOBBY=#ONT(outdoor)]': {
				'#GET_HOBBY`Interesting! When I\'m not working I love to read syfy-romance books.\n `': 'get_hobby_transition_two'
			},
			# observation = hobbies that involve just looking at something
			'[$USER_HOBBY=#ONT(observation)]': {
				'#GET_HOBBY`Interesting! When I\'m not working I love to read syfy-romance books.\n `': 'get_hobby_transition_two'
			},
			'error': {
				'`Sorry, I don\'t understand.`': 'get_hobby_transition_one'
			}
		}
	}


	# -- gets the user's hobby 2
	get_hobby_transition_two = {
		'state': 'get_hobby_transition_two',
		'`What other activities do you like to do for fun?`': {
			# get hobby #2
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
				'`Sorry, I don\'t understand.`': 'get_hobby_transition_two'
			}
		}
	}


	# -- gets the user's hobby 3
	get_hobby_transition_three = {
		'state': 'get_hobby_transition_three',
		'`Are there any other hobbies you\'re really passionate about?`': {
			# get hobby 3
			# learning = things that someone would learn for fun
			'[$USER_HOBBY=#ONT(learning)]': {
				'#GET_HOBBY`Nice.`': 'get_fav_color_transition_one'
			},
			# sports = a physical activity
			'[$USER_HOBBY=#ONT(sports)]': {
				'#GET_HOBBY`Nice.`': 'get_fav_color_transition_one'
			},
			# games = card/board games and the like
			'[$USER_HOBBY=#ONT(games)]': {
				'#GET_HOBBY`Nice.`': 'get_fav_color_transition_one'
			},
			# creative = creating something; an artistic hobby
			'[$USER_HOBBY=#ONT(creative)]': {
				'#GET_HOBBY`Nice.`': 'get_fav_color_transition_one'
			},
			# collecting = anything a person could collect
			'[$USER_HOBBY=#ONT(collecting)]': {
				'#GET_HOBBY`Nice.`': 'get_fav_color_transition_one'
			},
			# domestic = chores that are hobbies
			'[$USER_HOBBY=#ONT(domestic)]': {
				'#GET_HOBBY`Nice.`': 'get_fav_color_transition_one'
			},
			# making = making an object; tinkering
			'[$USER_HOBBY=#ONT(making)]': {
				'#GET_HOBBY`Nice.`': 'get_fav_color_transition_one'
			},
			# outdoor = hobbies that happen outdoors; that aren't sports
			'[$USER_HOBBY=#ONT(outdoor)]': {
				'#GET_HOBBY`Nice.`': 'get_fav_color_transition_one'
			},
			# observation = hobbies that involve just looking at something
			'[$USER_HOBBY=#ONT(observation)]': {
				'#GET_HOBBY`Nice.`': 'get_fav_color_transition_one'
			},
			'error': {
				'`Sorry, I don\'t understand.`': 'get_hobby_transition_three'
			}
		}
	}


	# -- gets the user's favourite colour #1
	get_fav_color_transition_one = {
		'state': 'get_fav_color_transition_one',
		# favourite colour #1
		'`While on the subject of things we like, it just occurred to me that I don\'t know your favorite color?!\n '
		' What is it?`': {
			'[$USER_COLOR=#ONT(red)]': {
				'#GET_FAV_COLOR`Oh, really? My favorite color is pink.\n '
				'It\'s so cute and works for a variety of fashion situations.\n`': 'get_fav_color_transition_two'
			},
			'[$USER_COLOR=#ONT(orange)]': {
				'#GET_FAV_COLOR`Oh, really? My favorite color is pink.\n '
				'It\'s so cute and works for a variety of fashion situations.\n`': 'get_fav_color_transition_two'
			},
			'[$USER_COLOR=#ONT(yellow)]': {
				'#GET_FAV_COLOR`Oh, really? My favorite color is pink.\n '
				'It\'s so cute and works for a variety of fashion situations.\n`': 'get_fav_color_transition_two'
			},
			'[$USER_COLOR=#ONT(green)]': {
				'#GET_FAV_COLOR`Oh, really? My favorite color is pink.\n '
				'It\'s so cute and works for a variety of fashion situations.\n`': 'get_fav_color_transition_two'
			},
			'[$USER_COLOR=#ONT(blue)]': {
				'#GET_FAV_COLOR`Oh, really? My favorite color is pink.\n '
				'It\'s so cute and works for a variety of fashion situations.\n`': 'get_fav_color_transition_two'
			},
			'[$USER_COLOR=#ONT(violet)]': {
				'#GET_FAV_COLOR`Oh, really? My favorite color is pink.\n '
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
				'I like`$USER_COLOR`too, it always stands out to me.`': 'get_not_fav_color_transition'
			},
			'[$USER_COLOR=#ONT(orange)]': {
				'#GET_FAV_COLOR`Lol, nice. ' 
				'I like`$USER_COLOR`too, it always stands out to me.`': 'get_not_fav_color_transition'
			},
			'[$USER_COLOR=#ONT(yellow)]': {
				'#GET_FAV_COLOR`Lol, nice. ' 
				'I like`$USER_COLOR`too, it always stands out to me.`': 'get_not_fav_color_transition'
			},
			'[$USER_COLOR=#ONT(green)]': {
				'#GET_FAV_COLOR`Lol, nice. ' 
				'I like`$USER_COLOR`too, it always stands out to me.`': 'get_not_fav_color_transition'
			},
			'[$USER_COLOR=#ONT(blue)]': {
				'#GET_FAV_COLOR`Lol, nice. ' 
				'I like`$USER_COLOR`too, it always stands out to me.`': 'get_not_fav_color_transition'
			},
			'[$USER_COLOR=#ONT(violet)]': {
				'#GET_FAV_COLOR`Lol, nice. ' 
				'I like`$USER_COLOR`too, it always stands out to me.`': 'get_not_fav_color_transition'
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
		'`Another thing I\'d love to know about you is how you like to dress. I\'m always curious about people\'s fashion preferences.\n '
		'Can you tell me a bit about your personal style?`': {
			'[$USER_STYLE=#ONT(sporty)]': {
				'#GET_STYLE`I\'m a fan of the sporty style too! People who dress sporty are effortlessly chic.\n `': 'get_style_transition_two'
			},
			'[$USER_STYLE=#ONT(bohemian)]': {
				'#GET_STYLE`I\'m not really a fan of the boheamian style, but I do love how cool people who dress in this style look.\n `': 'get_style_transition_two'
			},
			'[$USER_STYLE=#ONT(grunge)]': {
				'#GET_STYLE`The grunge style is so fun and edgy.\n `': 'get_style_transition_two'
			},
			'[$USER_STYLE=#ONT(preppy)]': {
				'#GET_STYLE`Lol, the preppy style is so \"academic\" of you! \U0001F602 \n `': 'get_style_transition_two'
			},
			'[$USER_STYLE=#ONT(punk)]': {
				'#GET_STYLE`I\'m a fan of the punk style too! Ik, surprising right?\n `': 'get_style_transition_two'
			},
			'[$USER_STYLE=#ONT(streetwear)]': {
				'#GET_STYLE`Streetwear is such a popular aesthetic these days, very cool you like it.\n `': 'get_style_transition_two'
			},
			'[$USER_STYLE=#ONT(classic)]': {
				'#GET_STYLE`Quite the \"classic\" person, huh? (See my joke there) Pretty cool how you like this style.\n `': 'get_style_transition_two'
			},
			'[$USER_STYLE=#ONT(casual)]': {
				'#GET_STYLE`Oh, so you like dressing casually? That\'s fun too.\n `': 'get_style_transition_two'
			},
			'[$USER_STYLE=#ONT(ethnic)]': {
				'#GET_STYLE`Pretty awesome how you represent your ethnicity in your clothes.\n `': 'get_style_transition_two'
			},
			'error': {
				'`Sorry, I don\'t understand`': 'get_style_transition_one'
			}
		}
	}
	

	# -- gets the user's favourite styles #2
	# TODO: add a statement here from Becca
	get_style_transition_two = {
		'state': 'get_style_transition_two',
		'`Is there another style you like to wear?`': {
			'[$USER_STYLE=#ONT(sporty)]': {
				'#GET_STYLE`comment.\n `': 'get_fav_clothing_transition'
			},
			'[$USER_STYLE=#ONT(bohemian)]': {
				'#GET_STYLE`comment.\n `': 'get_fav_clothing_transition'
			},
			'[$USER_STYLE=#ONT(grunge)]': {
				'#GET_STYLE`comment.\n `': 'get_fav_clothing_transition'
			},
			'[$USER_STYLE=#ONT(preppy)]': {
				'#GET_STYLE`comment.\n `': 'get_fav_clothing_transition'
			},
			'[$USER_STYLE=#ONT(punk)]': {
				'#GET_STYLE`comment.?\n `': 'get_fav_clothing_transition'
			},
			'[$USER_STYLE=#ONT(streetwear)]': {
				'#GET_STYLE`comment.\n `': 'get_fav_clothing_transition'
			},
			'[$USER_STYLE=#ONT(classic)]': {
				'#GET_STYLE`comment.\n `': 'get_fav_clothing_transition'
			},
			'[$USER_STYLE=#ONT(casual)]': {
				'#GET_STYLE`comment.\n `': 'get_fav_clothing_transition'
			},
			'[$USER_STYLE=#ONT(ethnic)]': {
				'#GET_STYLE`comment.\n `': 'get_fav_clothing_transition'
			},
			'error': {
				'`Sorry, I don\'t understand`': 'get_style_transition_two'
			}
		}
	}

	
	# -- get user's preferred clothing items (generic)
	get_fav_clothing_transition = {
		'state': 'get_fav_clothing_transition',
		'`What are some of clothing items you wear often?`': {
			'[$USER_FAV_CLOTHING_ITEM=#ONT(sporty)]': {
				'#GET_FAV_CLOTHING`comment.\n `': 'get_not_fav_clothing_transition'
			},
			'[$USER_FAV_CLOTHING_ITEM=#ONT(bohemian)]': {
				'#GET_FAV_CLOTHING`comment.\n `': 'get_not_fav_clothing_transition'
			},
			'[$USER_FAV_CLOTHING_ITEM=#ONT(grunge)]': {
				'#GET_FAV_CLOTHING`comment.\n `': 'get_not_fav_clothing_transition'
			},
			'[$USER_FAV_CLOTHING_ITEM=#ONT(preppy)]': {
				'#GET_FAV_CLOTHING`comment.\n `': 'get_not_fav_clothing_transition'
			},
			'[$USER_FAV_CLOTHING_ITEM=#ONT(punk)]': {
				'#GET_FAV_CLOTHING`comment.?\n `': 'get_not_fav_clothing_transition'
			},
			'[$USER_FAV_CLOTHING_ITEM=#ONT(streetwear)]': {
				'#GET_FAV_CLOTHING`comment.\n `': 'get_not_fav_clothing_transition'
			},
			'[$USER_FAV_CLOTHING_ITEM=#ONT(classic)]': {
				'#GET_FAV_CLOTHING`comment.\n `': 'get_not_fav_clothing_transition'
			},
			'[$USER_FAV_CLOTHING_ITEM=#ONT(casual)]': {
				'#GET_FAV_CLOTHING`comment.\n `': 'get_not_fav_clothing_transition'
			},
			'[$USER_FAV_CLOTHING_ITEM=#ONT(ethnic)]': {
				'#GET_FAV_CLOTHING`comment.\n `': 'get_not_fav_clothing_transition'
			},
			'error': {
				'`Sorry, I don\'t understand`': 'get_fav_clothing_transition'
			}
		}
	}


	# -- get user's not preferred clothing items (generic)
	get_not_fav_clothing_transition = {
		'state': 'get_not_fav_clothing_transition',
		'`What are some clothing items that you try to avoid?`': {
			'[$USER_NOT_FAV_CLOTHING_ITEM=#ONT(sporty)]': {
				'#GET_NOT_FAV_CLOTHING`comment.\n `': 'choice_recommendation_transition'
			},
			'[$USER_NOT_FAV_CLOTHING_ITEM=#ONT(bohemian)]': {
				'#GET_NOT_FAV_CLOTHING`comment.\n `': 'choice_recommendation_transition'
			},
			'[$USER_NOT_FAV_CLOTHING_ITEM=#ONT(grunge)]': {
				'#GET_NOT_FAV_CLOTHING`comment.\n `': 'choice_recommendation_transition'
			},
			'[$USER_NOT_FAV_CLOTHING_ITEM=#ONT(preppy)]': {
				'#GET_NOT_FAV_CLOTHING`comment.\n `': 'choice_recommendation_transition'
			},
			'[$USER_NOT_FAV_CLOTHING_ITEM=#ONT(punk)]': {
				'#GET_NOT_FAV_CLOTHING`comment.?\n `': 'choice_recommendation_transition'
			},
			'[$USER_NOT_FAV_CLOTHING_ITEM=#ONT(streetwear)]': {
				'#GET_NOT_FAV_CLOTHING`comment.\n `': 'choice_recommendation_transition'
			},
			'[$USER_NOT_FAV_CLOTHING_ITEM=#ONT(classic)]': {
				'#GET_NOT_FAV_CLOTHING`comment.\n `': 'choice_recommendation_transition'
			},
			'[$USER_NOT_FAV_CLOTHING_ITEM=#ONT(casual)]': {
				'#GET_NOT_FAV_CLOTHING`comment.\n `': 'choice_recommendation_transition'
			},
			'[$USER_NOT_FAV_CLOTHING_ITEM=#ONT(ethnic)]': {
				'#GET_NOT_FAV_CLOTHING`comment.\n `': 'choice_recommendation_transition'
			},
			'error': {
				'`Sorry, I don\'t understand`': 'get_not_fav_clothing_transition'
			}
		}
	}


	# -- ask if the user would like to be recommended an outfit 
	# or help getting styled with an outfit
	choice_recommendation_transition = {
		'state': 'choice_recommendation_transition',
		'`Alright, now that I\'ve collected all this information about you.\n '
		'Would you like me to recommend you an outfit? Or do you need styling advice for an oufit your currently wearing?`': {
			'{<recommend>, <outfit>}': {
				'`Alright!`#REC_OUTFIT`What do you think?`': {
					'#GET_FEEDBACK': {
						# TODO: fill out these statements
						'#IF($USER_SENTIMENT=positive)`I\'m happy you like it!`': 'end',
						'#IF($USER_SENTIMENT=neutral)`Cool....`': 'end',
						'#IF($USER_SENTIMENT=negative)`I\'m sorry you don\'t like it. Would you like me to recommend you another outfit?`': {
							'yes': {
								'`Okay, I can recommend you another outfit!`#REC_OUTFIT_AF_FEEDBACK`What do you think?`': 'end'
							},
							'no': {
								'`Alright, I won\'t give you any more recommendations.`': 'end'
							},
							'error': {
								'`Sorry, I don\'t understand.`': 'choice_recommendation_transition'
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
		'`what top are you currently wearing?`': {
			'[$USER_CURR_ITEM=#ONT(sporty)]': {
				'#GET_CURR_OUTFIT`Got it, nice! Let\'s move on to the next item of clothing.\n `': 'get_current_bottoms_transition'
			},
			'[$USER_CURR_ITEM=#ONT(bohemian)]': {
				'#GET_CURR_OUTFIT`Got it, nice! Let\'s move on to the next item of clothing.\n `': 'get_current_bottoms_transition'
			},
			'[$USER_CURR_ITEM=#ONT(grunge)]': {
				'#GET_CURR_OUTFIT`Got it, nice! Let\'s move on to the next item of clothing.\n `': 'get_current_bottoms_transition'
			},
			'[$USER_CURR_ITEM=#ONT(preppy)]': {
				'#GET_CURR_OUTFIT`Got it, nice! Let\'s move on to the next item of clothing.\n `': 'get_current_bottoms_transition'
			},
			'[$USER_CURR_ITEM=#ONT(punk)]': {
				'#GET_CURR_OUTFIT`Got it, nice! Let\'s move on to the next item of clothing.\n `': 'get_current_bottoms_transition'
			},
			'[$USER_CURR_ITEM=#ONT(streetwear)]': {
				'#GET_CURR_OUTFIT`Got it, nice! Let\'s move on to the next item of clothing.\n `': 'get_current_bottoms_transition'
			},
			'[$USER_CURR_ITEM=#ONT(classic)]': {
				'#GET_CURR_OUTFIT`Got it, nice! Let\'s move on to the next item of clothing.\n `': 'get_current_bottoms_transition'
			},
			'[$USER_CURR_ITEM=#ONT(casual)]': {
				'#GET_CURR_OUTFIT`Got it, nice! Let\'s move on to the next item of clothing.\n `': 'get_current_bottoms_transition'
			},
			'[$USER_CURR_ITEM=#ONT(ethnic)]': {
				'#GET_CURR_OUTFIT`Got it, nice! Let\'s move on to the next item of clothing.\n `': 'get_current_bottoms_transition'
			},
			# TODO: add more words that are similar to nothing, or have the same meaning
			# FIXME: what's up with the extra space? Try to remove.
			# if the user is wearing nothing, or something similar to nothing, return don't do anythgin in the current outfit dict
			'<nothing>': {
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
		'`What bottoms are you currently wearing?`': {
			'[$USER_CURR_ITEM=#ONT(sporty)]': {
				'#GET_CURR_OUTFIT`Understood. Moving on to the next item.\n `': 'get_current_coat_transition'
			},
			'[$USER_CURR_ITEM=#ONT(bohemian)]': {
				'#GET_CURR_OUTFIT`Understood. Moving on to the next item.\n `': 'get_current_coat_transition'
			},
			'[$USER_CURR_ITEM=#ONT(grunge)]': {
				'#GET_CURR_OUTFIT`Understood. Moving on to the next item.\n `': 'get_current_coat_transition'
			},
			'[$USER_CURR_ITEM=#ONT(preppy)]': {
				'#GET_CURR_OUTFIT`Understood. Moving on to the next item.\n `': 'get_current_coat_transition'
			},
			'[$USER_CURR_ITEM=#ONT(punk)]': {
				'#GET_CURR_OUTFIT`Understood. Moving on to the next item.\n `': 'get_current_coat_transition'
			},
			'[$USER_CURR_ITEM=#ONT(streetwear)]': {
				'#GET_CURR_OUTFIT`Understood. Moving on to the next item.\n `': 'get_current_coat_transition'
			},
			'[$USER_CURR_ITEM=#ONT(classic)]': {
				'#GET_CURR_OUTFIT`Understood. Moving on to the next item.\n `': 'get_current_coat_transition'
			},
			'[$USER_CURR_ITEM=#ONT(casual)]': {
				'#GET_CURR_OUTFIT`Understood. Moving on to the next item.\n `': 'get_current_coat_transition'
			},
			'[$USER_CURR_ITEM=#ONT(ethnic)]': {
				'#GET_CURR_OUTFIT`Understood. Moving on to the next item.\n `': 'get_current_coat_transition'
			},
			# TODO: add more words that are similar to nothing, or have the same meaning
			# if the user is wearing nothing, or something similar to nothing, return don't do anythgin in the current outfit dict
			'<nothing>': {
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
		'`What coat or outerwear are you currently wearing?`': {
			'[$USER_CURR_ITEM=#ONT(sporty)]': {
				'#GET_CURR_OUTFIT`Cool! And now...\n `': 'get_current_shoes_transition'
			},
			'[$USER_CURR_ITEM=#ONT(bohemian)]': {
				'#GET_CURR_OUTFIT`Cool! And now...\n `': 'get_current_shoes_transition'
			},
			'[$USER_CURR_ITEM=#ONT(grunge)]': {
				'#GET_CURR_OUTFIT`Cool! And now...\n `': 'get_current_shoes_transition'
			},
			'[$USER_CURR_ITEM=#ONT(preppy)]': {
				'#GET_CURR_OUTFIT`Cool! And now...\n `': 'get_current_shoes_transition'
			},
			'[$USER_CURR_ITEM=#ONT(punk)]': {
				'#GET_CURR_OUTFIT`Cool! And now...\n `': 'get_current_shoes_transition'
			},
			'[$USER_CURR_ITEM=#ONT(streetwear)]': {
				'#GET_CURR_OUTFIT`Cool! And now...\n `': 'get_current_shoes_transition'
			},
			'[$USER_CURR_ITEM=#ONT(classic)]': {
				'#GET_CURR_OUTFIT`Cool! And now...\n `': 'get_current_shoes_transition'
			},
			'[$USER_CURR_ITEM=#ONT(casual)]': {
				'#GET_CURR_OUTFIT`Cool! And now...\n `': 'get_current_shoes_transition'
			},
			'[$USER_CURR_ITEM=#ONT(ethnic)]': {
				'#GET_CURR_OUTFIT`Cool! And now...\n `': 'get_current_shoes_transition'
			},
			# TODO: add more words that are similar to nothing, or have the same meaning
			# if the user is wearing nothing, or something similar to nothing, return don't do anythgin in the current outfit dict
			'<nothing>': {
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
		'`What shoes are you currently wearing?`': {
			'[$USER_CURR_ITEM=#ONT(sporty)]': {
				'#GET_CURR_OUTFIT`Great, and last thing...\n `': 'get_current_accessory_transition'
			},
			'[$USER_CURR_ITEM=#ONT(bohemian)]': {
				'#GET_CURR_OUTFIT`Great, and last thing...\n `': 'get_current_accessory_transition'
			},
			'[$USER_CURR_ITEM=#ONT(grunge)]': {
				'#GET_CURR_OUTFIT`Great, and last thing...\n `': 'get_current_accessory_transition'
			},
			'[$USER_CURR_ITEM=#ONT(preppy)]': {
				'#GET_CURR_OUTFIT`Great, and last thing...\n `': 'get_current_accessory_transition'
			},
			'[$USER_CURR_ITEM=#ONT(punk)]': {
				'#GET_CURR_OUTFIT`Great, and last thing...\n `': 'get_current_accessory_transition'
			},
			'[$USER_CURR_ITEM=#ONT(streetwear)]': {
				'#GET_CURR_OUTFIT`Great, and last thing...\n `': 'get_current_accessory_transition'
			},
			'[$USER_CURR_ITEM=#ONT(classic)]': {
				'#GET_CURR_OUTFIT`Great, and last thing...\n `': 'get_current_accessory_transition'
			},
			'[$USER_CURR_ITEM=#ONT(casual)]': {
				'#GET_CURR_OUTFIT`Great, and last thing...\n `': 'get_current_accessory_transition'
			},
			'[$USER_CURR_ITEM=#ONT(ethnic)]': {
				'#GET_CURR_OUTFIT`Great, and last thing...\n `': 'get_current_accessory_transition'
			},
			# TODO: add more words that are similar to nothing, or have the same meaning
			# if the user is wearing nothing, or something similar to nothing, return don't do anythgin in the current outfit dict
			'<nothing>': {
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
		'`What accessory are you currently wearing?`': {
			'[$USER_CURR_ACCSRY=#ONT(sporty)]': {
				'#GET_CURR_OUTFIT`Awesome, thanks!\n `': 'choice_acessory_transition'
			},
			'[$USER_CURR_ACCSRY=#ONT(bohemian)]': {
				'#GET_CURR_OUTFIT`Awesome, thanks!\n `': 'choice_acessory_transition'
			},
			'[$USER_CURR_ACCSRY=#ONT(grunge)]': {
				'#GET_CURR_OUTFIT`Awesome, thanks!\n `': 'choice_acessory_transition'
			},
			'[$USER_CURR_ACCSRY=#ONT(preppy)]': {
				'#GET_CURR_OUTFIT`Awesome, thanks!\n `': 'choice_acessory_transition'
			},
			'[$USER_CURR_ACCSRY=#ONT(punk)]': {
				'#GET_CURR_OUTFIT`Awesome, thanks!\n `': 'choice_acessory_transition'
			},
			'[$USER_CURR_ACCSRY=#ONT(streetwear)]': {
				'#GET_CURR_OUTFIT`Awesome, thanks!\n `': 'choice_acessory_transition'
			},
			'[$USER_CURR_ACCSRY=#ONT(classic)]': {
				'#GET_CURR_OUTFIT`Awesome, thanks!\n `': 'choice_acessory_transition'
			},
			'[$USER_CURR_ACCSRY=#ONT(casual)]': {
				'#GET_CURR_OUTFIT`Awesome, thanks!\n `': 'choice_acessory_transition'
			},
			'[$USER_CURR_ACCSRY=#ONT(ethnic)]': {
				'#GET_CURR_OUTFIT`Awesome, thanks!\n `': 'choice_acessory_transition'
			},
			# TODO: add more words that are similar to nothing, or have the same meaning
			# if the user is wearing nothing, or something similar to nothing, return don't do anythgin in the current outfit dict
			'<nothing>': {
				'$USER_CURR_ITEM=""#GET_CURR_OUTFIT`Okay, so you\'re not wearing that item. I can work with that.\n `': 'choice_acessory_transition'
			},
			'error': {
				'`I\'m not sure I understand.`': 'get_current_accessory_transition'
			}
		}
	}


	choice_acessory_transition = {
		'state': 'choice_acessory_transition',
		'`Are you wearing any more accessories?`': {
			'<yes>': 'get_current_accessory_transition',
			'<no>': 'return_current_outfit_advice_transition'
		}
	}


	# -- given the user's current oufit, recommend a clothing item that would go with it
	return_current_outfit_advice_transition = {
		'state': 'return_current_outfit_advice_transition',
		'`Alright, given the information I\'ve recived about what you\'re currently wearing,`#REC_CLOTHING_ITEM`What do you think?`': {
			# TODO: add more reponse here
			'#GET_FEEDBACK': {
				'#IF($USER_SENTIMENT=positive)`I\'m happy you like it!`': 'end',
				'#IF($USER_SENTIMENT=neutral)`Cool....`': 'end',
				'#IF($USER_SENTIMENT=negative)`I\'m sorry you don\'t like it. Would you like me to recommend you another outfit?`': {
					'yes': {
						'`Okay, I can recommend you another outfit!`#REC_CLOTHING_ITEM_AF_FEEDBACK`What do you think?`': 'end'
					},
					'no': {
						'`Alright, I won\'t give you any more recommendations.`': 'end'
					},
					'error': {
						'`Sorry, I don\'t understand.`': 'choice_recommendation_transition'
					}
				}
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
		# macros from  openai_macros.py ============================================
		'REC_OUTFIT': MacroRecommendOutfit(),
		'GET_FEEDBACK': MacroReturnFeedbackSentiment(),
		'REC_OUTFIT_AF_FEEDBACK':MacroRecommendOutfitAfterFeedback(),
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
	df.load_transitions(babble_transition)

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
	df.load_transitions(return_current_outfit_advice_transition)

	df.add_macros(macros)

	return df


# run dialogue ======================================================
if __name__ == '__main__':
	# save(main_dialogue(), 'users-pickle.pkl')
	load(main_dialogue(), 'users-pickle.pkl')
