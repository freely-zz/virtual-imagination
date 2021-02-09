from gym.envs.registration import register

register(
    id='dpp-v0',
    entry_point='gym_dpp.envs:DPP',
)

register(
    id='dpp-v1',
    entry_point='gym_dpp.envs:DPP1',
)

register(
    id='dpp-v2',
    entry_point='gym_dpp.envs:DPP2',
)

register(
    id='dpp-v3',
    entry_point='gym_dpp.envs:DPP3',
)
