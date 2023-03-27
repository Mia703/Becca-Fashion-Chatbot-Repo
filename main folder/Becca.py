import pandas as pd
from typing import Dict, Any, List
from emora_stdm import Macro, Ngrams, DialogueFlow


# variables ======================================================

# macros ======================================================

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
			'<"black tie">': {
				'`Got it. You have a black tie event right? '
				'\n Black tie events are usually a formal event that usually requires men to wear a tuxedo '
				'and women to wear an evening gown.`': 'end'
			},
			'<"white tie">': {
				'`Got it. You have a white tie event right? '
				'\n White tie events are the most formal dress code and usually requires men to wear a black tailcoat,'
				' a white bow tie, and black trousers, and women to wear a floor-length formal gown.`': 'end'
			},
			'<"cocktail">': {
				'`Got it. You have a cocktail event right? '
				'\n Cocktail events are a semi-formal event where men typically wear a suit and tie '
				'and women wear a cocktail dress or a dressy skirt and blouse.`': 'end'
			},
			'<"business formal">': {
				'`Got it. You have a business formal event right? '
				'\n Business formal events are a dress code for professional settings, such as a job interview, '
				'where men typically wear a suit and tie and women wear a suit, dress or blouse and skirt.`': 'end'
			},
			'<"business casual">': {
				'`Got it. You have a business casual event right?` '
				'\n Business casual events are less formal than business formal but still requires professional attire, '
				'such as slacks and a button-down shirt for men and a skirt or '
				'dress pants with a blouse or sweater for women.': 'end'
			},
			'error': {
				'`Sorry, I don\'t understand`': 'end'
			}
		}
	}

	# macro references ======================================================
	macros = {

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
