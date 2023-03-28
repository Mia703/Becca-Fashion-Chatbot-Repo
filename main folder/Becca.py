import pandas as pd
from typing import Dict, Any, List
from emora_stdm import Macro, Ngrams, DialogueFlow

# variables ======================================================

# macros ======================================================

# the dialogue ======================================================
def main_dialogue() -> DialogueFlow:
	# introduction to the bot and what she does
	introduction_transition = {
		'state': 'start',
		'`Hi, my name is Becca! I\'m a personal stylist bot created just for you! \n'
		'I\'m here to help you look good and feel good about you and your clothes. \n'
		'And just an F.Y.I. the information you share with me will stay with me ;) \n'
		'So, let\'s get started! `': 'choice_transition'
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
		'`But wait, you\'ve got two options. \n'
		'If you want, we can talk about any dress-code specific events you\'re going to attend or \n'
		'we can just jump right into me getting to know you more. \n'
		'This is so I can give you better style recommendations later. \n'
		'What do you want to do?`': {
			'<[dress, code]>': {
				'`Okay, we can talk about your upcoming event.`': 'dresscode_transition'
			},
			'<{style, clothes}>': {
				'`Okay, we can get to styling you. \n'
				'In order to give you good recommendations, I need to get to know you and your personal style first. \n'
				'To start, I wanna get to know your lifestyle and interests. \n'
				'Anything you share with me will affect my recommendations later, '
				'but anyway, let\'s get started. `': 'end'
			}
		},
		'error': {
			'`Sorry, I don\'t understand.`': 'clothing_transition'
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
		'`I know that a lot of young people have a hard time understanding the rules of a dress-code specific events. \n'
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

	# macro references ======================================================
	macros = {

	}

	# ======================================================
	df = DialogueFlow('start', end_state='end')
	df.load_transitions(introduction_transition)
	df.load_transitions(choice_transition)
	df.load_transitions(clothing_transition)
	df.load_transitions(babble_transition)
	df.load_transitions(dresscode_transition)

	df.add_macros(macros)

	return df


# run dialogue ======================================================
if __name__ == '__main__':
	main_dialogue().run()
