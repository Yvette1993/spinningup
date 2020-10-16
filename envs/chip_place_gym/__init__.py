from gym.envs.registration import register
register(
    id='chip_place_env-v0',                                   # Format should be xxx-v0, xxx-v1....
    entry_point='chip_place_gym.envs:ChipPlaceEnv',              # Expalined in envs/__init__.py
)
