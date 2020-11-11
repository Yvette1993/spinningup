#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Time: 2020/10/29 17:02:02
# Author: Yingying Li
import itertools
import numpy as np
from .chip_place_env import ChipPlaceEnv
from .chip_place_env import RED,BLACK,GREEN
from .chip_place_env import is_index

class ConnectEnv(ChipPlaceEnv):
    def __init__(self, board_shape = 8, dsp_number=2, illegal_action_mode='pass',render_characters='-+ox'):
        super().__init__(board_shape=board_shape,
                illegal_action_mode=illegal_action_mode,
                render_characters=render_characters)
        self.dsp_number=dsp_number
    
    ## get wirelength
    def get_hpwl(self, node, other_node):
        l_x     = []
        l_y     = []
        l_x.append(node['x']) 
        l_y.append(node['y'])
        l_x.append(other_node['x'])
        l_y.append(other_node['y'])
        min_x = min (l_x)
        max_x = max (l_x)
        min_y = min (l_y)
        max_y = max (l_y)
        hpwl  = max_x - min_x + max_y - min_y
        return hpwl

    def get_other_node(self, indx):
        for node in self.Data:
            if node['id'] == indx:
                return node
            else:
                raise ValueError("Not responding node!")
            

    def get_reward(self, state, mode='HPWL'):
        wirelength=0.0
        #直接通过self.Data计算线长
        for node  in self.Data:
            for indx in node['adj']:
                other_node = self.get_other_node(indx)
                hpwl = self.get_hpwl(node, other_node)
                wirelength += hpwl
        return wirelength

        ## show line

        



        




        
        
  
        


