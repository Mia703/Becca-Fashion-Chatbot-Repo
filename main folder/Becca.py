import pickle
import macros
import re
import pandas as pd
from typing import Dict, Any, List
from emora_stdm import Macro, Ngrams, DialogueFlow



# the dialogue ======================================================
def main_dialogue() -> DialogueFlow:
	# introduction to the bot and what she does
	introduction_transition = {
		'state': 'start',
		'`What\'s your name?`': {
			# get the user's name -- to either create or return their dictionary
			'#GET_NAME': {
				# return "nice to meet you" or "welcome back" message
				'#RETURN_WELCOME_MESG': 'choice_transition'
			},
			'error': {
				'`Sorry, I don\'t understand.`': 'start'
			}
		}
	}

	# do you wanna talk about clothes or babble?
	choice_transition = {
		'state': 'choice_transition',
		'`Would you like to talk about the movie \"Babbel\" or shall we talk about clothes?`': {
			# Let's talk about clothes
			'[{let, lets, wanna, want}, clothes]': {
				'`Okay, we can talk about clothes! \n`': 'clothing_transition'
			},
			# Let's talk about the movie Babble
			'<babbel>': {
				'`Okay, we can talk about the movie Babble! \n`': 'babble_transition'
			},
			'error': {
				'`Sorry, I don\'t understand.`': 'choice_transition'
			}
		}
	}

	# let's talk about clothes -- introduction
	clothing_transition = {
		'state': 'clothing_transition',
		'`If you want, I can help you define what to wear to a dress-code specific event \n'
		'or we can just start talking about you. But before I can start styling you,'
		' I need to get to know you and your lifestyle first. \n'
		'To start I wanna know more about your hobbies. \n What do you want to do?`': {
			'<[dress, code]>': {
				'`Okay, we can talk about your upcoming event.`': 'dresscode_transition'
			},
			'<{style, styling}>': {
				'`Okay, we can get to styling you.`': 'hobbies_transition'
			},
			'error': {
				'`Sorry, I don\'t understand.`': 'clothing_transition'
			}
		}
	}

	# let's talk about babble -- introduction
	babble_transition = {
		'state': 'babble_transition',
		'`The movie \"Babble\" was pretty interesting, wasn\'t it?`': 'end'
	}

	# dress-code topic
	dresscode_transition = {
		'state': 'dresscode_transition',
		'`Okay, let\'s talk about dress codes. \n'
		'I know that a lot of young people have a hard time defining what to wear to a dress-code specific event. \n'
		'I\'ll help you decipher it! What event are you going to?`': {
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
				'`Sorry, I don\'t understand`': 'dresscode_transition'
			}
		}
	}

	# hobbies transition
	hobbies_transition = {
		'state': 'hobbies_transition',
		'`Let\'s talk about hobbies.`': 'end'
	}

	# macro references ======================================================
	main_macros = {
		'GET_NAME': macros.MacroGetName(),
		'RETURN_WELCOME_MESG': macros.MacroWelcomeMessage(),
	}

	# ======================================================
	df = DialogueFlow('start', end_state='end')
	df.load_transitions(introduction_transition)
	df.load_transitions(choice_transition)
	df.load_transitions(clothing_transition)
	df.load_transitions(babble_transition)
	df.load_transitions(dresscode_transition)
	df.load_transitions(hobbies_transition)

	df.add_macros(main_macros)

	return df


# run dialogue ======================================================
if __name__ == '__main__':
	main_dialogue().run()
