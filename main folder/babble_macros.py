# 'SET_WATCH_STATUS': MacroGPTJSON(
# 			'Has the speaker watched the movie?',
# 			{V.WATCH_STATUS.name: "yes"},
# 			{V.WATCH_STATUS.name: "no"}),
# 		'SET_SPEAKER_RATING': MacroGPTJSON(
# 			'Does the speaker like, dislike, or feel indifferent about the movie? Reply "positive" if user likes the movie, "neutral" if user feels indifferent and "negative" if user does not like the movie.',
# 			{V.USER_RATING.name: "positive"},
# 			{V.USER_RATING.name: "N/A"},
# 		),
# 		'SET_PERM_HOURS': MacroGPTJSON(
# 			'Does the speaker want a perm on Friday at 10:00, Friday at 11:00, Friday at 13:00, Friday at 14:00, Saturday at 10:00, or Saturday at 14:00? Reply "no" if none of these time slots are given.',
# 			{V.valid_perm.name: "yes"},
# 			{V.valid_perm.name: "no"},
# 		),
# 		'SET_DYE_HOURS': MacroGPTJSON(
# 			'Does the speaker want to dye hair on Wednesday at 10:00, Wednesday at 11:00, Wednesday at 13:00, Thursday at 10:00, or Thursday at 11:00? Reply "no" if none of these time slots are given.',
# 			{V.valid_dye.name: "yes"},
# 			{V.valid_dye.name: "no"},
# 		)