# imports ============================================
import pickle
import re
import random
import json
import pandas as pd
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
		return True


# depending on if the user is a returner or a new users
# a different message will appear
# if new user creates new user dictionary
class MacroWelcomeMessage(Macro):
	def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
		global users_dictionary
		global current_user

		print("The current user is " + current_user)

		# if the user is not already in the dictionary
		# create a dictionary with the user's name
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

			return str('Nice to meet you ' + current_user.capitalize() + 
			'. My name is Becca! '
			'I\'m a personal stylist bot created just for you.\n '
			'I\'m here to help you look good and feel good about yourself and your clothes.\n '
			'And just an F.Y.I. the information you share with me will stay with me. \U0001F92B\n '
			'So, let\'s get started!')

		# else, the user is already in the dictionary -- returning user
		else:
			print("A returning user: " + current_user)
			return str('Welcome back ' + current_user.capitalize() + '!\n ')


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
		# if needed
		# TODO: maybe remove? not really using...
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


# dialogue ============================================
def main_dialogue() -> DialogueFlow:
	introduction_transition = {
		'state': 'start',
		'`Hi, what\'s your name?`': {
			'#GET_NAME': {
				'#RETURN_WELCOME_MESG': 'get_current_top_outfit_transition'
			}
		}
	}


	# do you wanna talk about the movie or clothes?
	choice_transition = {
		'state': 'choice_transition',
		'`Would you like to talk about the movie \"Babble\" or shall we talk about you and your clothes?`': {
			# Let's talk about the movie Babble
			'<babble>': {
				'`Okay, we can talk about the movie \"Babble\"!`': 'babble_transition'
			},
			# Let's talk about clothes
			'[{let, lets, wanna, want}, clothes]': {
				'`Okay, we can talk about clothes!\n`': 'clothing_transition'
			},
			'error': {
				'`Sorry, I don\'t understand.`': 'choice_transition'
			}
		}
	}


	# let's talk about Babble
	babble_transition = {
		'state': 'babble_transition',
		'`That movie tho`': 'end'
		# TODO: anywhere in the conversation insert "summary" indicator 
		# which will prompt the system to give a summary of the film
	}


	# let's talk about clothing
	clothing_transition = {
		'state': 'clothing_transition',
		'`As a fashion bot, my main function is to recommend you clothes based on your preferences and lifestyle.\n '
		'To give you good recommendations, I need to get to know you first.\n '
		'Note, anything you share will affect my recommendation later, but anyway, let\'s get started!\n`': 'get_age_transition'
		# TODO: if user is not a new user skip to recommendation transition -- THE FUTURE
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


# FIXME: change to style onology?
	# -- get user's preferred clothing items (generic)
	get_fav_clothing_transition = {
		'state': 'get_fav_clothing_transition',
		'`What are some of clothing items you wear often?`': {
			'[$USER_FAV_CLOTHING_ITEM=#ONT(basics)]': {
				'#GET_FAV_CLOTHING`The necessities are important! I\'ll admit I\'m honestly quite the basic girl myself lol.\n `': 'get_not_fav_clothing_transition'
			},
			'[$USER_FAV_CLOTHING_ITEM=#ONT(dressy)]': {
				'#GET_FAV_CLOTHING`I like to dress up too! In my opinion, being overdressed is always best.\n `': 'get_fav_clothing_transition'
			},
			'[$USER_FAV_CLOTHING_ITEM=#ONT(casual)]': {
				'#GET_FAV_CLOTHING`Casual\'s nice, but I\'m personally an overdresser. The grocery store is my runway!\n `': 'get_not_fav_clothing_transition'
			},
			'[$USER_FAV_CLOTHING_ITEM=#ONT(outerwear)]': {
				'#GET_FAV_CLOTHING`I don\'t typically wear a lot of coats and jackets and stuff because in Atlanta it\'s usually warm here!\n `': 'get_not_fav_clothing_transition'
			},
			'error': {
				'`Sorry, I don\'t understand.`': 'get_fav_clothing_transition'
			}
		}
	}


# FIXME: change to style onology?
	# -- get user's not preferred clothing items (generic)
	get_not_fav_clothing_transition = {
		'state': 'get_not_fav_clothing_transition',
		'`What are some clothing items that you try to avoid?`': {
			'[$USER_NOT_FAV_CLOTHING_ITEM=#ONT(basics)]': {
				'#GET_NOT_FAV_CLOTHING`I see, so you\'re not basic girl like me then. We\'ll have to agree to disagree.\n `': 'get_current_top_outfit_transition'
			},
			'[$USER_NOT_FAV_CLOTHING_ITEM=#ONT(dressy)]': {
				'#GET_NOT_FAV_CLOTHING`That\'s too bad that you don\'t like to dress up. Playing dress up in my closet is my favorite activity.\n `': 'get_current_top_outfit_transition'
			},
			'[$USER_NOT_FAV_CLOTHING_ITEM=#ONT(casual)]': {
				'#GET_NOT_FAV_CLOTHING`I\'m glad that we\'re on the same page. Casual is boring.\n `': 'get_current_top_outfit_transition'
			},
			'[$USER_NOT_FAV_CLOTHING_ITEM=#ONT(outerwear)]': {
				'#GET_NOT_FAV_CLOTHING`I don\'t wear too much outerwear either. It\'s warm where I live so I tend not to need many layers.\n `': 'get_current_top_outfit_transition'
			},
			'error': {
				'`Sorry, I don\'t understand.`': 'get_not_fav_clothing_transition'
			}
		}
	}


	# -- get user's current outfit #1
	# -- get the top the user is wearing
	get_current_top_outfit_transition = {
		'state': 'get_current_top_outfit_transition',
		'`What top are you currently wearing?`': {
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


	# TODO: maybe do the same thing for hobbies, favourite colour, and style?
	choice_acessory_transition = {
		'state': 'choice_acessory_transition',
		'`Are you wearing any more accessories?`': {
			'<yes>': 'get_current_accessory_transition',
			'<no>': 'end'
		}
	}


	# macro references ============================================
	macros = {
		'GET_NAME': MacroGetName(),
		'RETURN_WELCOME_MESG': MacroWelcomeMessage(),
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
	}

	# ============================================
	df = DialogueFlow('start', end_state='end')

	df.knowledge_base().load_json_file('./resources/occupation_ontology.json')
	df.knowledge_base().load_json_file('./resources/hobbies_ontology.json')
	df.knowledge_base().load_json_file('./resources/color_names_ontology.json')
	df.knowledge_base().load_json_file('./resources/styles_ontology.json')
	df.knowledge_base().load_json_file('./resources/clothing_items_ontology.json')

	df.load_transitions(introduction_transition)

	df.load_transitions(choice_transition)
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
	df.load_transitions(get_current_top_outfit_transition)
	df.load_transitions(get_current_bottoms_transition)
	df.load_transitions(get_current_coat_transition)
	df.load_transitions(get_current_shoes_transition)
	df.load_transitions(get_current_accessory_transition)

	# ask if the user is wearing any more accessories
	# if yes, double back to get_current_accessory_transition
	# if no, move on to next transition
	df.load_transitions(choice_acessory_transition)

	df.add_macros(macros)

	return df


# run dialogue ======================================================
if __name__ == '__main__':
	# save(main_dialogue(), 'users-pickle.pkl')
	load(main_dialogue(), 'users-pickle.pkl')
