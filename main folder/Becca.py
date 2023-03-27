import csv
import re
from typing import Dict, Any, List
from emora_stdm import Macro, Ngrams, DialogueFlow


# variables ======================================================

# the word I'm looking for
keyword = ""

# macros ======================================================

# searches for the keyword in the csv file
class MacroSearchKeyword(Macro):
	def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[str]):
		global keyword

		print(ngrams.raw_text())
		return


# the dialogue ======================================================
def main_dialogue() -> DialogueFlow:
	main_transition = {
		'state': 'start',
		'`Hi, my name is Becca!`': 'introduction_transition'
	}

	# introduction to the bot and what she does
	introduction_transition = {
		'state': 'introduction_transition',
		'`I\'m a personal stylist bot created just for you! \n'
		'I\'m here to help you look good and feel good about your clothes. \n'
		'But before I can get started styling you, I need to get to know you and your personal style. \n'
		'And just an F.Y.I. all the information you share with me will stay with me. ;) \n'
		'So let\'s get started!`': 'dresscode_transition'
	}


	# dress-code topic
	dresscode_transition = {
		'state': 'dresscode_transition',
		'`\n \nI know that a lot of young people have a hard time understanding the rules of a dress-code specific event. \n'
		'I\'ll help you decipher it! Do you have any upcoming dress-code specific events?`': {
			# '#RETURN_DRESS_CODE': {
			# 	'`Got it.`': 'end'
			# },
			# '{<"black tie">, <"white tie">, <"cocktail">, <"business formal">, <"business casual">}': {
			# 	'`Got it` #RETURN_DRESS_CODE': 'end'
			# },
			'{<"black tie">, <"black-tie">}': {
				'`Got it. You have a black tie event right?`': 'end'
			},
			'error': {
				'`Sorry, I don\'t understand`': 'end'
			}
		}
	}

	# macro references ======================================================
	macros = {
		'RETURN_DRESS_CODE': MacroSearchKeyword(),
	}

	# ======================================================
	df = DialogueFlow('start', end_state='end')
	df.load_transitions(main_transition)
	df.load_transitions(introduction_transition)
	df.load_transitions(dresscode_transition)

	df.add_macros(macros)

	return df

# run dialogue ======================================================
if __name__ == '__main__':
	main_dialogue().run()
