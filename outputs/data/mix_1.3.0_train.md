# Dataset report — `mix_1.3.0_train` (data/processed_1.3.0, train, 93,509 conversations)

| source | conversations | share_of_mix | multi_turn_share | mean_turn_pairs | mean_reply_words | duplicate_share | quality_rejection_share | emotional_user_turn_share | rewrite_request_share | eval_prompt_overlap |
|---|---|---|---|---|---|---|---|---|---|---|
| behaviour | 2336 | 0.025 | 0.199 | 1.35 | 14.2 | 0.0 | 0.0 | 0.441 | 0.001 | 0 |
| blended_skill_talk | 7229 | 0.077 | 0.894 | 3.42 | 13.4 | 0.0 | 0.0 | 0.066 | 0.0 | 0 |
| coedit | 14929 | 0.16 | 0.0 | 1 | 17.4 | 0.097 | 0.0 | 0.0 | 0.987 | 0 |
| conversation | 2380 | 0.025 | 0.324 | 1.61 | 20.4 | 0.75 | 0.0 | 0.007 | 0.0 | 0 |
| curated | 3561 | 0.038 | 0.45 | 1.95 | 14.4 | 0.7 | 0.002 | 0.183 | 0.001 | 0 |
| dailydialog | 7318 | 0.078 | 0.853 | 3.07 | 11.5 | 0.0 | 0.0 | 0.035 | 0.0 | 0 |
| dialogue_skills | 3280 | 0.035 | 0.845 | 2.68 | 8.0 | 0.5 | 0.0 | 0.037 | 0.001 | 0 |
| email | 400 | 0.004 | 0.0 | 1 | 41.3 | 0.475 | 0.0 | 0.0 | 0.0 | 0 |
| empathetic_dialogues | 19597 | 0.21 | 0.99 | 2.05 | 11.3 | 0.0 | 0.0 | 0.196 | 0.0 | 0 |
| everyday_conversations | 6008 | 0.064 | 0.718 | 2.7 | 21.6 | 0.5 | 0.0 | 0.023 | 0.0 | 0 |
| handwritten | 9364 | 0.1 | 0.0 | 1 | 10.9 | 0.27 | 0.0 | 0.0 | 0.982 | 0 |
| oasst1 | 1432 | 0.015 | 0.0 | 1 | 53.9 | 0.0 | 0.0 | 0.02 | 0.0 | 0 |
| paradetox | 2551 | 0.027 | 0.0 | 1 | 9.0 | 0.0 | 0.0 | 0.0 | 1.0 | 0 |
| prosocial_dialog | 6000 | 0.064 | 0.0 | 1 | 26.1 | 0.0 | 0.0 | 0.113 | 0.0 | 0 |
| smol_rewrite | 1428 | 0.015 | 0.0 | 1 | 42.2 | 0.186 | 0.001 | 0.003 | 0.987 | 0 |
| smoltalk | 5696 | 0.061 | 0.0 | 1 | 58.6 | 0.0 | 0.0 | 0.03 | 0.001 | 0 |

Emotion detection uses the rule-based analyzer (English heuristics); shares are approximate.

- **behaviour**: emotions {'anxiety': 0.13, 'sadness': 0.069, 'grief': 0.058, 'disappointment': 0.054, 'frustration': 0.042, 'anger': 0.03, 'excitement': 0.028, 'confusion': 0.02, 'loneliness': 0.01}; quality rejections -; schema ok
- **blended_skill_talk**: emotions {'anxiety': 0.017, 'happiness': 0.016, 'excitement': 0.01, 'sadness': 0.009, 'frustration': 0.005, 'grief': 0.004, 'anger': 0.003, 'disappointment': 0.002, 'confusion': 0.001, 'loneliness': 0.001}; quality rejections -; schema ok
- **coedit**: emotions {'anxiety': 0.0, 'disappointment': 0.0}; quality rejections {'assistant_mostly_non_letters': 2, 'assistant_too_short': 1}; schema ok
- **conversation**: emotions {'anxiety': 0.003, 'excitement': 0.002, 'confusion': 0.001, 'frustration': 0.001}; quality rejections -; schema ok
- **curated**: emotions {'sadness': 0.066, 'loneliness': 0.038, 'anxiety': 0.024, 'excitement': 0.022, 'frustration': 0.012, 'anger': 0.01, 'happiness': 0.006, 'confusion': 0.005}; quality rejections {'assistant_mostly_non_letters': 6}; schema ok
- **dailydialog**: emotions {'anxiety': 0.009, 'excitement': 0.008, 'happiness': 0.007, 'sadness': 0.005, 'frustration': 0.002, 'anger': 0.001, 'grief': 0.001, 'confusion': 0.001, 'disappointment': 0.0}; quality rejections -; schema ok
- **dialogue_skills**: emotions {'sadness': 0.036, 'happiness': 0.002}; quality rejections -; schema ok
- **email**: emotions -; quality rejections -; schema ok
- **empathetic_dialogues**: emotions {'sadness': 0.037, 'anxiety': 0.037, 'happiness': 0.035, 'excitement': 0.029, 'anger': 0.018, 'frustration': 0.013, 'grief': 0.012, 'disappointment': 0.006, 'loneliness': 0.006, 'confusion': 0.002}; quality rejections -; schema ok
- **everyday_conversations**: emotions {'anxiety': 0.019, 'excitement': 0.002, 'happiness': 0.001, 'sadness': 0.001, 'frustration': 0.001, 'confusion': 0.001}; quality rejections -; schema ok
- **handwritten**: emotions {'sadness': 0.0}; quality rejections -; schema ok
- **oasst1**: emotions {'confusion': 0.006, 'anxiety': 0.003, 'excitement': 0.003, 'happiness': 0.001, 'frustration': 0.001, 'disappointment': 0.001, 'anger': 0.001, 'sadness': 0.001, 'grief': 0.001, 'loneliness': 0.001}; quality rejections -; schema ok
- **paradetox**: emotions -; quality rejections {'assistant_contains_url': 1}; schema ok
- **prosocial_dialog**: emotions {'sadness': 0.025, 'frustration': 0.022, 'anger': 0.018, 'anxiety': 0.015, 'excitement': 0.008, 'happiness': 0.008, 'confusion': 0.007, 'grief': 0.005, 'disappointment': 0.003, 'loneliness': 0.002}; quality rejections -; schema ok
- **smol_rewrite**: emotions {'happiness': 0.001, 'excitement': 0.001}; quality rejections {'assistant_contains_url': 2}; schema ok
- **smoltalk**: emotions {'anxiety': 0.01, 'happiness': 0.005, 'excitement': 0.005, 'sadness': 0.004, 'confusion': 0.002, 'frustration': 0.002, 'disappointment': 0.001, 'anger': 0.001, 'loneliness': 0.001, 'grief': 0.001}; quality rejections -; schema ok
