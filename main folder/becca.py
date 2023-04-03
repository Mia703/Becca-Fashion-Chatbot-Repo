# imports ============================================
import pickle
import re
import random
import pandas as pd
from typing import Dict, Any, List
from collections import defaultdict
from emora_stdm import Macro, Ngrams, DialogueFlow

# variables ============================================
users_dictionary = {}
current_user = ""

# imports the csv file
color_names_dataframe = pd.read_csv('./resources/color_names.csv')


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
# also creates user dictionary
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
		user_nested_list = user_nested_dictionary["hobbies_list"]

		# append the hobby to the list
		user_nested_list.append(user_hobby)

		print(users_dictionary)


# save the user's favourite colours 
class MacroSaveFavoriteColor(Macro):
	def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
		global users_dictionary
		global current_user
		global color_names_dataframe

		# get the user's colour
		user_colour_name = str(vars['USER_COLOR'])

		# TODO: search the dataframe for the HEX code of the colour name
		user_colour_hex = 0

		# access the user's dictionary
		user_nested_dictionary = users_dictionary[current_user]

		# access the user's favourite colour list
		user_nested_list = user_nested_dictionary["fav_colors_list"]

		# append the HEX code to the list
		user_nested_list.append(user_colour_hex)

		print(users_dictionary)


# save the user's not favourite colours
class MacroSaveNotFavoriteColor(Macro):
	def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
		global users_dictionary
		global current_user
		global color_names_dataframe

		# get the user's not favourite colour
		# user_colour_name = star(vars[''])

		# search the dataframe for the HEX code of the colour name
		# user_colour_hex = 0;

		# access the user's dictionary
		# user_nested_dictionary = users_dictionary[current_user]

		# access the user's not favourite colour list
		# user_nested_list = user_nested_dictionary["not_fav_colors_list"]

		# append the HEX code to the list
		# user_nested_list.append(user_colour_hex)

		# print(users_dictionary)



# saves the user's favourite styles
class MacroSaveStyle(Macro):
	def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
		global users_dictionary
		global current_user


# saves the user's favourite clothing items
class MacroSaveFavoriteClothing(Macro):
	def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
		global users_dictionary
		global current_user


# saves the user's not favourite clothing items
class MacroSaveNotFavoriteClothing(Macro):
	def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
		global users_dictionary
		global current_user



# saves the user's current outfit
class MacroSaveOutfit(Macro):
	def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
		global users_dictionary
		global current_user

		print(ngrams)
		print(vars)
		print(args)

		return "hello"



# pickle
#  functions ============================================

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
		print(users_dictionary)
		df.run()
		save(df, varfile)


# clear the dictionary
def clear_dictionary(dict_name: Dict):
	dict_name.clear()


# dialogue ============================================
def main_dialogue() -> DialogueFlow:
	introduction_transition = {
		'state': 'start',
		'`Hi, what\'s your name?`': {
			'#GET_NAME': {
				# '#RETURN_WELCOME_MESG': 'choice_transition'
				'#RETURN_WELCOME_MESG': 'get_hobby_transition_one'
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
	}


	# let's talk about clothing
	clothing_transition = {
		'state': 'clothing_transition',
		'`As a fashion bot, my main function is to recommend you clothes based on your preferences and lifestyle.\n '
		'To give you good recommendations, I need to get to know you first.\n '
		'Note, anything you share will affect my recommendation later, but anyway, let\'s get started!\n\n`': 'get_age_transition'
		# TODO: if user is not a new user skip to recommendation transition -- THE FUTURE
	}

	
	# personal information -- basic questions
	# -- get user's age
	get_age_transition = {
		'state': 'get_age_transition',
		'`To be direct, how old are you?`': {
			'#GET_AGE': {
				'#RETURN_AGE_RESPONSE': 'get_occupation_transition'
			}
		}
	}

	# -- get user's occupation
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
							'error': {
								'`Oh, nice`': 'get_hobby_transition_one'
							}
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


	# -- get user's hobby 1
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


	# -- get user's hobby 2
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


	# -- get user's hobby 3
	get_hobby_transition_three = {
		'state': 'get_hobby_transition_three',
		'`Are there any other hobbies you\'re really passionate about?`': {
			# get hobby 3
			# learning = things that someone would learn for fun
			'[$USER_HOBBY=#ONT(learning)]': {
				'#GET_HOBBY`Nice.`': 'get_fav_color_transition'
			},
			# sports = a physical activity
			'[$USER_HOBBY=#ONT(sports)]': {
				'#GET_HOBBY`Nice.`': 'get_fav_color_transition'
			},
			# games = card/board games and the like
			'[$USER_HOBBY=#ONT(games)]': {
				'#GET_HOBBY`Nice.`': 'get_fav_color_transition'
			},
			# creative = creating something; an artistic hobby
			'[$USER_HOBBY=#ONT(creative)]': {
				'#GET_HOBBY`Nice.`': 'get_fav_color_transition'
			},
			# collecting = anything a person could collect
			'[$USER_HOBBY=#ONT(collecting)]': {
				'#GET_HOBBY`Nice.`': 'get_fav_color_transition'
			},
			# domestic = chores that are hobbies
			'[$USER_HOBBY=#ONT(domestic)]': {
				'#GET_HOBBY`Nice.`': 'get_fav_color_transition'
			},
			# making = making an object; tinkering
			'[$USER_HOBBY=#ONT(making)]': {
				'#GET_HOBBY`Nice.`': 'get_fav_color_transition'
			},
			# outdoor = hobbies that happen outdoors; that aren't sports
			'[$USER_HOBBY=#ONT(outdoor)]': {
				'#GET_HOBBY`Nice.`': 'get_fav_color_transition'
			},
			# observation = hobbies that involve just looking at something
			'[$USER_HOBBY=#ONT(observation)]': {
				'#GET_HOBBY`Nice.`': 'get_fav_color_transition'
			},
			'error': {
				'`Sorry, I don\'t understand.`': 'get_hobby_transition_three'
			}
		}
	}

	# -- get user's favourite colour
	get_fav_color_transition_one = {
		'state': 'get_fav_color_transition',
		# favourite colour #1
		'`While on the subject of things we like, it just occured to me that I don\'t know your favorite color?!\n '
		' What is it?`': {
			'[$USER_COLOR=#ONT(red)]': {
				'`Oh, really? My favorite color is pink. It\'s so cute and works for a variety of fashion situations.`': 'get_fav_color_transition_two'
			},
			'[$USER_COLOR=#ONT(orange)]': {
				'`Oh, really? My favorite color is pink. It\'s so cute and works for a variety of fashion situations.`': 'get_fav_color_transition_two'
			},
			'[$USER_COLOR=#ONT(yellow)]': {
				'`Oh, really? My favorite color is pink. It\'s so cute and works for a variety of fashion situations.`': 'get_fav_color_transition_two'
			},
			'[$USER_COLOR=#ONT(green)]': {
				'`Oh, really? My favorite color is pink. It\'s so cute and works for a variety of fashion situations.`': 'get_fav_color_transition_two'
			},
			'[$USER_COLOR=#ONT(blue)]': {
				'`Oh, really? My favorite color is pink. It\'s so cute and works for a variety of fashion situations.`': 'get_fav_color_transition_two'
			},
			'[$USER_COLOR=#ONT(violet)]': {
				'`Oh, really? My favorite color is pink. It\'s so cute and works for a variety of fashion situations.`': 'get_fav_color_transition_two'
			},
			'error': {
				'`Sorry, I don\'t understand.`': 'get_fav_color_transition'
			}
		}
	}

	get_fav_color_transition_two = {
		'state': 'get_fav_color_transition_two',
		# favourite colour #2
		'`Is there another color you love to wear?`': {
			'[$USER_COLOR=#ONT(red)]': {
				'`Lol, nice. I like`$USER_COLOR`too, it always stands out to me.`': 'end'
			},
			'[$USER_COLOR=#ONT(orange)]': {
				'`Lol, nice. I like`$USER_COLOR`too, it always stands out to me.`': 'end'
			},
			'[$USER_COLOR=#ONT(yellow)]': {
				'`Lol, nice. I like`$USER_COLOR`too, it always stands out to me.`': 'end'
			},
			'[$USER_COLOR=#ONT(green)]': {
				'`Lol, nice. I like`$USER_COLOR`too, it always stands out to me.`': 'end'
			},
			'[$USER_COLOR=#ONT(blue)]': {
				'`Lol, nice. I like`$USER_COLOR`too, it always stands out to me.`': 'end'
			},
			'[$USER_COLOR=#ONT(violet)]': {
				'`Lol, nice. I like`$USER_COLOR`too, it always stands out to me.`': 'end'
			},
			'error': {
				'`Sorry, I don\'t understand.`': 'get_fav_color_transition_two'
			}
		}
	}

	# TODO: -- get user's not favourite colours
	get_not_fav_color_transition = {
		'state': 'get_not_fav_color_transition',
		'`What are some colors you hate or colors you would love to avoid?`': 'end'
	}

	# TODO: -- get user's preferred styles
	get_style_transition = {
		'state': 'get_style_transition',
		'`What styles do you prefer?`': 'end'
	}


	# TODO: -- get user's preferred clothing items (generic)
	get_fav_clothing_transition = {
		'state': 'get_fav_clothing_transition',
		'`What are some of clothing items you wear often?`': 'end'
	}


	# TODO: -- get user's not preferred clothing items (generic)
	get_not_fav_clothing_transition = {
		'state': 'get_not_fav_clothing_transition',
		'`What are some clothing items that you try to avoid?`': 'end'
	}


	# TODO: -- get user's current outfit
	get_current_outfit_transition = {
		'state': 'get_current_outfit_transition',
		'`What are you currently wearing?`': {
			# I don't care what the user says here
			'error': {
				'`Okay.` #GET_CURR_OUTFIT': 'end'
			}
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
	df.knowledge_base().load_json_file('./resources/color_ontology.json')

	df.load_transitions(introduction_transition)

	df.load_transitions(choice_transition)
	df.load_transitions(babble_transition)

	df.load_transitions(clothing_transition)

	df.load_transitions(get_age_transition)
	df.load_transitions(get_occupation_transition)
	
	df.load_transitions(get_hobby_transition_one)
	df.load_transitions(get_hobby_transition_two)
	df.load_transitions(get_hobby_transition_three)

	df.load_transitions(get_fav_color_transition_one)
	df.load_transitions(get_fav_color_transition_two)

	df.load_global_nlu(get_not_fav_color_transition)

	df.load_transitions(get_style_transition)

	df.load_transitions(get_fav_clothing_transition)
	df.load_transitions(get_not_fav_clothing_transition)

	df.load_transitions(get_current_outfit_transition)

	df.add_macros(macros)

	return df


# run dialogue ======================================================
if __name__ == '__main__':
	# save(main_dialogue(), 'users-pickle.pkl')
	load(main_dialogue(), 'users-pickle.pkl')
