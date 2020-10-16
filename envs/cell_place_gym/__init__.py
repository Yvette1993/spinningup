from gym.envs.registration import register

register(
    id='cell_place_env-v0',                                   # Format should be xxx-v0, xxx-v1....
    entry_point='cell_place_gym.envs:CellPlaceEnv',              # Expalined in envs/__init__.py
)
