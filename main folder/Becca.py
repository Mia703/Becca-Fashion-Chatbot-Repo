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
			return str('Nice to meet you ' + current_user.capitalize())

		# else, the user is already in the dictionary -- returning user
		else:
			print ("A returning user: " + current_user)
			return str('Welcome back ' + current_user.capitalize())


# pickle functions ============================================

def save(df: DialogueFlow, varfile: str):
	global users_dictionary

	with open(varfile, 'wb') as handle:
		df.run()
		d = {k: v for k, v in df.vars().items() if not k.startswith('_')}
		pickle.dump(d, handle, protocol=pickle.HIGHEST_PROTOCOL)
		pickle.dump(users_dictionary, handle, protocol=pickle.HIGHEST_PROTOCOL)


def load(df:DialogueFlow, varfile:str):
	global users_dictionary

	with open(varfile, 'rb') as handle:
		d = pickle.load(handle)
		df.vars().update(d)
		users_dictionary = pickle.load(handle)
		print(users_dictionary)
		df.run()
		save(df, varfile)


# clear the dictionary
def clear_dictionary (dict_name: Dict):
	dict_name.clear()


# dialogue ============================================
def main_dialogue() -> DialogueFlow:
	introduction_transition = {
		'state': 'start',
		'`What\'s your name?`': {
			'#GET_NAME': {
				'#RETURN_WELCOME_MESG': 'end'
			}
		}
	}

	# macro references ============================================
	macros = {
		'GET_NAME': MacroGetName(),
		'RETURN_WELCOME_MESG': MacroWelcomeMessage(),

	}

	# ============================================
	df = DialogueFlow('start', end_state='end')
	df.load_transitions(introduction_transition)

	df.add_macros(macros)

	return df


# run dialogue ======================================================
if __name__ == '__main__':
	# save(main_dialogue(), 'users-pickle.pkl')
	load(main_dialogue(), 'users-pickle.pkl')