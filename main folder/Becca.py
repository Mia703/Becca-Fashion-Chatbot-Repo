# imports ============================================
import pickle
import re
import pandas as pd
from typing import Dict, Any, List
from emora_stdm import Macro, Ngrams, DialogueFlow

# variables ============================================
users_dictionary = {}
current_user = ""


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
				uinterests=[],
				fcolours=[],
				wardrobe={},
				current_outfit={}
			)
			return str('Nice to meet you ' + current_user.capitalize() + '!\n '
																		 'My name is Becca. '
																		 'I\'m a personal stylist bot '
																		 'created just for you!\n I\'m here to help you '
																		 'look good and feel good about you and '
																		 'your clothes.\n And just an F.Y.I. the '
																		 'information you share with me '
																		 'will stay with me ;)\n '
																		 'So, let\'s get started!')

		# else, the user is already in the dictionary -- returning user
		else:
			print("A returning user: " + current_user)
			return str('Welcome back ' + current_user.capitalize() + '!\n ')


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
		'`What\'s your name?`': {
			'#GET_NAME': {
				'#RETURN_WELCOME_MESG': 'choice_transition'
			}
		}
	}

	# do you wanna talk about the movie or clothes?
	choice_transition = {
		'state': 'choice_transition',
		'`Would you like to talk about the movie \"Babble\" or shall we talk about clothes?`': {
			# Let's talk about clothes
			'[{let, lets, wanna, want}, clothes]': {
				'`Okay, we can talk about clothes!\n`': 'clothing_transition'
			},
			# Let's talk about the movie Babble
			'<babble>': {
				'`Okay, we can talk about the movie \"Babble\"!`': 'babble_transition'
			},
			'error': {
				'`Sorry, I don\'t understand.`': 'choice_transition'
			}
		}
	}

	# let's talk about clothing
	clothing_transition = {
		'state': 'clothing_transition',
		'`As a fashion bot, my main function is to recommend you clothes based on your preferences and lifestyle.\n '
		'But I also know a lot of young people have a hard time figuring out'
		' what to wear to for a specific dress-code.\n '
		'So, what would you like to do?\n '
		'I can get to styling you or I can answer your question about dress-codes.`': {
			'<[dress, code]>': {
				'`Okay, I can answer your questions about dress codes.`': 'end'
			},
			'<{style, styling, clothes}>': {
				'`Okay, I can get started styling you!\n '
				'In order to give you good recommendations, I need to get to know you and your personal style first.\n '
				'To start, I wanna learn more about your lifestyle and hobbies.\n '
				'Anything you share will affect my recommendations later, but anyway, let\'s get started.`': 'end'
			},
			'error': {
				'`Sorry, I don\'t understand.\n`': 'clothing_transition'
			}
		}
	}

	# let's talk about Babble
	babble_transition = {
		'state': 'babble_transition',
	}

	# macro references ============================================
	macros = {
		'GET_NAME': MacroGetName(),
		'RETURN_WELCOME_MESG': MacroWelcomeMessage(),

	}

	# ============================================
	df = DialogueFlow('start', end_state='end')
	df.load_transitions(introduction_transition)
	df.load_transitions(choice_transition)
	df.load_transitions(clothing_transition)
	df.load_transitions(babble_transition)

	df.add_macros(macros)

	return df


# run dialogue ======================================================
if __name__ == '__main__':
	# save(main_dialogue(), 'users-pickle.pkl')
	load(main_dialogue(), 'users-pickle.pkl')
