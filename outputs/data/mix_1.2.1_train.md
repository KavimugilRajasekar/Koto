# Dataset report — `mix_1.2.1_train` (data/processed_1.2.1, train, 133,300 conversations)

| source | conversations | share_of_mix | multi_turn_share | mean_turn_pairs | mean_reply_words | duplicate_share | quality_rejection_share | emotional_user_turn_share | rewrite_request_share | eval_prompt_overlap |
|---|---|---|---|---|---|---|---|---|---|---|
| behaviour | 2227 | 0.017 | 0.178 | 1.33 | 14.4 | 0.0 | 0.0 | 0.451 | 0.0 | 0 |
| blended_skill_talk | 7250 | 0.054 | 0.894 | 3.42 | 13.4 | 0.0 | 0.002 | 0.064 | 0.0 | 0 |
| coedit | 27872 | 0.209 | 0.0 | 1 | 17.0 | 0.123 | 0.0 | 0.001 | 0.983 | 0 |
| conversation | 2444 | 0.018 | 0.345 | 1.64 | 20.4 | 0.75 | 0.0 | 0.006 | 0.0 | 0 |
| curated | 3585 | 0.027 | 0.453 | 1.95 | 14.3 | 0.698 | 0.002 | 0.183 | 0.001 | 0 |
| dailydialog | 7397 | 0.055 | 0.855 | 3.08 | 11.4 | 0.0 | 0.008 | 0.035 | 0.0 | 0 |
| dialogue_skills | 3320 | 0.025 | 0.842 | 2.67 | 7.9 | 0.5 | 0.0 | 0.001 | 0.0 | 0 |
| email | 400 | 0.003 | 0.0 | 1 | 40.9 | 0.47 | 0.0 | 0.0 | 0.0 | 0 |
| empathetic_dialogues | 19639 | 0.147 | 0.99 | 2.05 | 11.3 | 0.0 | 0.002 | 0.193 | 0.0 | 0 |
| everyday_conversations | 6010 | 0.045 | 0.718 | 2.7 | 21.6 | 0.5 | 0.0 | 0.021 | 0.0 | 0 |
| handwritten | 18576 | 0.139 | 0.0 | 1 | 10.6 | 0.422 | 0.0 | 0.0 | 0.989 | 0 |
| oasst1 | 2993 | 0.022 | 0.0 | 1 | 54.5 | 0.0 | 0.024 | 0.018 | 0.001 | 0 |
| paradetox | 4067 | 0.031 | 0.0 | 1 | 8.9 | 0.0 | 0.0 | 0.0 | 1.0 | 0 |
| prosocial_dialog | 6000 | 0.045 | 0.0 | 1 | 26.1 | 0.0 | 0.0 | 0.115 | 0.0 | 0 |
| smol_rewrite | 2434 | 0.018 | 0.0 | 1 | 41.4 | 0.281 | 0.002 | 0.004 | 0.986 | 0 |
| smoltalk | 19086 | 0.143 | 0.0 | 1 | 58.0 | 0.0 | 0.006 | 0.027 | 0.001 | 0 |

Emotion detection uses the rule-based analyzer (English heuristics); shares are approximate.

- **behaviour**: emotions {'anxiety': 0.136, 'sadness': 0.076, 'grief': 0.058, 'disappointment': 0.051, 'frustration': 0.047, 'anger': 0.029, 'excitement': 0.027, 'confusion': 0.019, 'loneliness': 0.01}; quality rejections -; schema ok
- **blended_skill_talk**: emotions {'anxiety': 0.018, 'happiness': 0.015, 'excitement': 0.011, 'sadness': 0.006, 'grief': 0.004, 'frustration': 0.004, 'anger': 0.003, 'disappointment': 0.002, 'loneliness': 0.001, 'confusion': 0.001}; quality rejections {'assistant_contains_url': 5, 'assistant_too_short': 2, 'assistant_mostly_non_letters': 10}; schema ok
- **coedit**: emotions {'grief': 0.001, 'frustration': 0.0, 'anxiety': 0.0}; quality rejections {'assistant_mostly_non_letters': 5, 'assistant_too_short': 2, 'assistant_repeats_sentence': 2, 'assistant_contains_url': 2}; schema ok
- **conversation**: emotions {'anxiety': 0.003, 'excitement': 0.002, 'frustration': 0.001}; quality rejections -; schema ok
- **curated**: emotions {'sadness': 0.06, 'loneliness': 0.045, 'anxiety': 0.022, 'excitement': 0.018, 'anger': 0.016, 'frustration': 0.009, 'happiness': 0.006, 'confusion': 0.005}; quality rejections {'assistant_mostly_non_letters': 6}; schema ok
- **dailydialog**: emotions {'anxiety': 0.011, 'happiness': 0.008, 'excitement': 0.006, 'sadness': 0.003, 'confusion': 0.002, 'frustration': 0.002, 'anger': 0.002, 'grief': 0.001, 'disappointment': 0.001, 'loneliness': 0.0}; quality rejections {'assistant_mostly_non_letters': 55, 'assistant_repeats_sentence': 3, 'assistant_contains_url': 2}; schema ok
- **dialogue_skills**: emotions {'happiness': 0.001}; quality rejections -; schema ok
- **email**: emotions -; quality rejections -; schema ok
- **empathetic_dialogues**: emotions {'anxiety': 0.043, 'happiness': 0.035, 'sadness': 0.034, 'excitement': 0.029, 'anger': 0.014, 'frustration': 0.013, 'grief': 0.013, 'disappointment': 0.006, 'loneliness': 0.005, 'confusion': 0.002}; quality rejections {'assistant_mostly_non_letters': 13, 'assistant_too_short': 13, 'assistant_contains_url': 26}; schema ok
- **everyday_conversations**: emotions {'anxiety': 0.016, 'excitement': 0.001, 'confusion': 0.001, 'frustration': 0.001, 'happiness': 0.001, 'sadness': 0.001, 'loneliness': 0.0}; quality rejections {'assistant_mostly_non_letters': 2}; schema ok
- **handwritten**: emotions -; quality rejections -; schema ok
- **oasst1**: emotions {'confusion': 0.005, 'anxiety': 0.003, 'excitement': 0.002, 'happiness': 0.002, 'sadness': 0.002, 'loneliness': 0.001, 'grief': 0.001, 'frustration': 0.001, 'anger': 0.001, 'disappointment': 0.001}; quality rejections {'assistant_contains_url': 54, 'assistant_mostly_non_letters': 19, 'assistant_too_short': 5}; schema ok
- **paradetox**: emotions -; quality rejections {'assistant_mostly_non_letters': 2}; schema ok
- **prosocial_dialog**: emotions {'sadness': 0.026, 'frustration': 0.022, 'anger': 0.016, 'anxiety': 0.015, 'happiness': 0.01, 'excitement': 0.009, 'grief': 0.006, 'confusion': 0.005, 'disappointment': 0.003, 'loneliness': 0.003}; quality rejections -; schema ok
- **smol_rewrite**: emotions {'excitement': 0.002, 'sadness': 0.001, 'happiness': 0.0, 'frustration': 0.0, 'anxiety': 0.0}; quality rejections {'assistant_contains_url': 4}; schema ok
- **smoltalk**: emotions {'anxiety': 0.009, 'excitement': 0.004, 'happiness': 0.004, 'sadness': 0.002, 'grief': 0.002, 'loneliness': 0.002, 'confusion': 0.002, 'disappointment': 0.002, 'anger': 0.001, 'frustration': 0.001}; quality rejections {'assistant_mostly_non_letters': 87, 'assistant_too_short': 35, 'assistant_repeats_sentence': 6, 'assistant_contains_url': 11}; schema ok
