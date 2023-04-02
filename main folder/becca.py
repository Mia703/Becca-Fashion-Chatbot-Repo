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
color_names_dataframe = pd.read_csv('./resources/color_names_no_duplicates.csv')


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
				fav_clothes_list=[],
				not_fav_clothes_list=[],
				style_list=[],
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
			return str('So, your an adult adult. I can still help!\n')
		
		else:
			return str('Omg, you\'re old! Ah, I mean, you\'re so mature...\n I can still help you though.\n')


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
					'How you got into that field?']

		# tell me more...
		return str('Oh, okay! For me, I love my job!\n '
		'As a fashion bot, I\'m always looking for new ways to communicate better and connect with my users,\n '
		'especially since I was born a month ago. \U0001F609 ' + random.choice(responses))


# saves the user's hobbies
class MacroSaveHobby(Macro):
	def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
		global users_dictionary
		global current_user

		# prints only one match -- print(vars['USER_HOBBY'])
		user_hobby = str(vars['USER_HOBBY'])

		# save the user's occupation
		# users_dictionary[current_user]['hobbies_list'].append("hello")
		print(users_dictionary)


# save the user's favourite colours 
class MacroSaveFavoriteColor(Macro):
	def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
		global users_dictionary
		global current_user
		global color_names_dataframe

		# prints the first 5 and the last 5 rows of the dataframe
		# print(color_names_dataframe)

		# prints the entire dataframe
		# print(color_names_dataframe.to_string())

		# TODO: search the dataframe for the colours the user listed -- reference deprecated.txt
		return str(ngrams.text())

		# TODO: save the colours to the user's dictionary



class MacroSaveNotFavoriteColor(Macro):
	def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
		global users_dictionary
		global current_user
		global color_names_dataframe

		# prints the first 5 and the last 5 rows of the dataframe
		# print(color_names_dataframe)

		# prints the entire dataframe
		# print(color_names_dataframe.to_string())

		# TODO: search the dataframe for the colours the user listed -- reference deprecated.txt
		return str(ngrams.text())

		# TODO: save the colours to the user's dictionary



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
				'#RETURN_WELCOME_MESG': 'get_fav_color_transition'
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
							'error': 'get_hobby_transition'
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
							'error': 'get_hobby_transition'
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
							'error': 'get_hobby_transition'
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
							'error': 'get_hobby_transition'
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
							'error': 'get_hobby_transition'
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
							'error': 'get_hobby_transition'
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
							'error': 'get_hobby_transition'
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
								'`Oh, nice`': 'get_hobby_transition'
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
							'error': 'get_hobby_transition'
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
							'error': 'get_hobby_transition'
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
							'error': 'get_hobby_transition'
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
							'error': 'get_hobby_transition'
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
							'error': 'get_hobby_transition'
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
							'error': 'get_hobby_transition'
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
							'error': 'get_hobby_transition'
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
							'error': 'get_hobby_transition'
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
							'error': 'get_hobby_transition'
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
							'error': 'get_hobby_transition'
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
							'error': 'get_hobby_transition'
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
							'error': 'get_hobby_transition'
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
							'error': 'get_hobby_transition'
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
							'error': 'get_hobby_transition'
						}
					}
				}
			},
			'error': {
				'`I don\'t know much about that field, but it sounds like you must have a lot of expertise!`': 'end'
			}
		}
	}


	# -- get user's hobbies
	get_hobby_transition = {
		'state': 'get_hobby_transition',
		# FIXME: how do I save multiple ontology matches? - It only returns the last match
		'`What do you do when you\'re not working? In other words, what are some of your hobbies?`': {
			# learning = things that someone would learn for furn
			'[$USER_HOBBY=#ONT(learning)]': {
				'`Oh, nice. I also love` $USER_HOBBY\n ': 'get_fav_color_transition'
			},
			# sports = a physical activity
			'[$USER_HOBBY=#ONT(sports)]': {
				'`Oh, nice. I also love` $USER_HOBBY\n ': 'get_fav_color_transition'
			},
			# games = card/board games and the like
			'[$USER_HOBBY=#ONT(games)]': {
				'`Oh, nice. I also love` $USER_HOBBY\n ': 'get_fav_color_transition'
			},
			# creative = creating something; an artistic hobby
			'[$USER_HOBBY=#ONT(creative)]': {
				'`Oh, nice. I also love` $USER_HOBBY\n ': 'get_fav_color_transition'
			},
			# collecting = anything a person could collect
			'[$USER_HOBBY=#ONT(collecting)]': {
				'`Oh, nice. I also love` $USER_HOBBY\n ': 'get_fav_color_transition'
			},
			# domestic = chores that are hobbies
			'[$USER_HOBBY=#ONT(domestic)]': {
				'`Oh, nice. I also love` $USER_HOBBY\n ': 'get_fav_color_transition'
			},
			# making = making an object; tinkering
			'[$USER_HOBBY=#ONT(making)]': {
				'`Oh, nice. I also love` $USER_HOBBY\n ': 'get_fav_color_transition'
			},
			# outdoor = hobbies that happen outdoors; that aren't sports
			'[$USER_HOBBY=#ONT(outdoor)]': {
				'`Oh, nice. I also love` $USER_HOBBY\n ': 'get_fav_color_transition'
			},
			# observation = hobbies that involve just looking at something
			'[$USER_HOBBY=#ONT(observation)]': {
				'`Oh, nice. I also love` $USER_HOBBY\n ': 'get_fav_color_transition'
			},
			'error': {
				'`Sorry, I don\'t understand.`': 'hobbies_transition'
			}
		}
	}


	get_fav_color_transition = {
		'state': 'get_fav_color_transition',
		'`What are some of your favorite colors?`': {
			'#GET_FAV_COLOR': 'end'
		}
	}

	get_not_fav_color_transition = {
		'state': 'get_not_fav_color_transition',
		'`What are some colors you hate or colors you would love to avoid?`': 'end'
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
	}

	# ============================================
	df = DialogueFlow('start', end_state='end')

	df.knowledge_base().load_json_file('./resources/occupation_ontology.json')
	df.knowledge_base().load_json_file('./resources/hobbies_ontology.json')

	df.load_transitions(introduction_transition)
	df.load_transitions(choice_transition)
	df.load_transitions(babble_transition)
	df.load_transitions(clothing_transition)
	df.load_transitions(get_age_transition)
	df.load_transitions(get_occupation_transition)
	df.load_transitions(get_hobby_transition)
	df.load_transitions(get_fav_color_transition)

	df.add_macros(macros)

	return df


# run dialogue ======================================================
if __name__ == '__main__':
	# save(main_dialogue(), 'users-pickle.pkl')
	load(main_dialogue(), 'users-pickle.pkl')
