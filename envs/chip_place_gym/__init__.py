#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Time: 2020/10/28 17:51:44
# Author: Yingying Li
from gym.envs.registration import register

register(
    id='chip_place_env-v0',                                   # Format should be xxx-v0, xxx-v1....
    entry_point='chip_place_gym.envs:ChipPlaceEnv',              # Expalined in envs/__init__.py
)