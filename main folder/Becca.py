from emora_stdm import DialogueFlow
from typing import Dict, Any
from Resources import Macros


def matching_strategies() -> Dict[str, Any]:
	return {
		'state': 'start',
		'`Hello. How are you?`': {
			'[{good, fantastic}]': {
				'`Glad to hear that you are doing well :)`': 'end'
			},
			'[{bad, could be better}]': {
				'`I hope your day gets better soon :(`': 'end'
			},
			'[{how, and}, {you, going}]': {
				'`I feel superb. Thank you!`': 'end'
			},
			'error': {
				'`Sorry, I didn\'t understand you.`': 'end'
			},
		}
	}


df = DialogueFlow('start', end_state='end')
df.load_transitions(matching_strategies())

if __name__ == '__main__':
	df.run()
