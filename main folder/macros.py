import pickle
import macros
import re
import pandas as pd
from typing import Dict, Any, List
from emora_stdm import Macro, Ngrams, DialogueFlow

# variables ======================================================
users_dictionary = {}
current_user = ""


# macros ======================================================

# saves and returns the user's name
class MacroGetName(Macro):
	def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
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

		# update the current user string
		current_user = firstname

		vars['TITLE'] = title
		vars['FIRSTNAME'] = firstname.capitalize()
		vars['LASTNAME'] = lastname
		return True


class MacroWelcomeMessage(Macro):
	def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
		global users_dictionary
		global current_user

		# if the current user is not already in the dictionary
		# create a dictionary with the user's first name
		if users_dictionary.get(current_user) is None:
			users_dictionary[current_user] = dict(name=str(current_user.capitalize()), hobbies=[], fcolours=[],
												  wardrobe={})

			print(users_dictionary)

			return str('Nice to meet you '
					   + current_user.capitalize() + '! '
													 'My name is Becca! '
													 'I\'m a personal stylist bot created just for you! \n '
													 'I\'m here to help you look good and feel good about you '
													 'and your clothes. \n '
													 'And just an F.Y.I. any and all information you share with me '
													 'will stay with me ;). \n So let\'s get started!')

		# else, the current user alreay has a dictionary -- returning user
		else:
			return str('Welcome back ' + current_user.capitalize())
