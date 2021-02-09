# DPP_Gym_Environment
Grid-based deceptive path-planning environment for AI-GYM.
Dependencies: numpy, random, math,time

import gym_dpp
gym.make('dpp-v0') #optimal
gym.make('dpp-v1') #ambiguous
gym.make('dpp-v2') #simulating
gym.make('dpp-v3') #extended GR

To run simulations post-install:
modify calling script (last line of qlearn.py) to select required gym version and run:
python qlearn.py
