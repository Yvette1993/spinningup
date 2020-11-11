#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Time: 2020/10/28 17:49:44
# Author: Yingying Li
import os
import sys
import copy
from six import StringIO
import numpy as np
import gym
from gym import spaces
from chip_place_gym.envs import connect 
from chip_place_gym.native import load_data


EMPTY = 0 
BLACK = -1   # input
GREEN = 1    # output
RED = 2          # dsp

def strfboard(board, render_characters='-+ox', end='\n'):
    """
    Format a board as a string
    
    Parameters
    ----
    board : np.array
    render_characters : str
    end : str
    
    Returns
    ----
    s : str
    """
    s = ''
    for x in range(board.shape[0]):
        for y in range(board.shape[1]):
            c = render_characters[board[x][y]]
            s += c
        s += end
    return s[:-len(end)]

def is_index(board, location):
        if len(location) != 2:
            return False
        x,y = location
        return x in range(board.shape[0]) and y in range(board.shape[1])

class ChipPlaceEnv(gym.Env):
    metadata = {"render.modes": ["ansi", "human"]}

    ## 代表退出放置器件的动作
    RESIGN = np.array([-1, -1])

    ##Gym库扩展要求的接口
    root = os.getcwd()
    file_path = os.path.join(root, 'test.yaml')

    #构造函数，确定观测空间动作空间
    def __init__(self, board_shape, illegal_action_mode='resign', render_characters='-+ox', allow_pass=True, data_path = file_path):
        self.allow_pass = allow_pass
        data =load_data.LoadData(data_path)
        Data  = load_data.LoadData.get_DAG_data(data)   # include input, output and dsp
        self.Data = Data
        # valid_node = []
        # for node in Data:
        #     if node['type'] not in ['input', 'output']:
        #         valid_node.append(node)
        # self.Valid_node = valid_node    # don't include input and output, but include others nodes. 
        self.T = len(self.Data)
         
        if illegal_action_mode == 'resign':
            self.illegal_equivalent_action = self.RESIGN
        else:
            raise ValueError()

        self.render_characters = {device : render_characters[device] for device in [EMPTY, BLACK, GREEN, RED  ]}

        if isinstance(board_shape, int):
            board_shape = (board_shape, board_shape)
        assert len(board_shape) == 2 # invalid board shape
        self.board = np.zeros(board_shape)
        assert self.board.size >1

        ##定义观测空间和动作空间
        observation_space = [
            spaces.Box(low=-1, high=2, shape=board_shape, dtype=np.int8),
            spaces.Box(low=-1, high=2, shape=(), dtype=np.int8)
        ]
        self.observation_space  = spaces.Tuple(observation_space)  #观测空间
        action_space = [
            spaces.Box(low=-np.ones((2,)),
                        high=np.array(board_shape), dtype=np.int8),
        ]
        self.action_space = spaces.Tuple(action_space)  # 动作空间

    # 初始化随机数生成器，不需要也要重写
    def seed(self, seed=None):
        return []

    #初始化环境
    def reset(self):
        self.board = np.zeros_like(self.board, dtype=np.int8) 
        for y in range(4):
            self.board[0][y] = BLACK  # input nodes
            for node in self.Data:
                if node['id'] == y and node['type'] == 'input':
                    node['y'] = y
        
        self.board[-1][-2] = GREEN  # output node
        for node in self.Data:
            if node['type'] == 'output':
                node['y'] = self.board[0][-2]
                node['x'] = self.board[0][-1]
             
        self.device = RED
        return self.board, self.device

    #下一步状态和动作
    def is_valid(self, state, action):
        board, _ = state
        if not is_index(board, action):
            return False
        x, y = action
        return board[x, y] == EMPTY

    def get_reward(self, state, mode='HPWL'):
        wirelength = connect.ConnectEnv.get_reward(self, state)
        return -wirelength

    def get_next_state(self, state, action):
        """
        Get the next state.
        
        Parameters
        ----
        state : (np.array, int)    board and current device
        action : np.array    location and skip indicator
        
        Returns
        ----
        next_state : (np.array, int)    next board and next device
        
        Raise
        ----
        ValueError : location in action is not valid
        """
        board, device = state
        x, y = action
        if self.is_valid(state, action):
            board = copy.deepcopy(board)
            board[x, y] = device
            #把相应的x,y更新到self.Data
            for node in self.Data:
                if node['type'] == 'dsp':
                    if node['x'] == 'None':
                        node['x'] = x
                        node['y'] = y
                        break
        return board, -device

    def next_step(self, state, action):
        """
        Get the next observation, reward, done, and info.
        
        Parameters
        ----
        state : (np.array, int)    board and current player
        action : np.array    location
        
        Returns
        ----
        next_state : (np.array, int)    next board and next player
        reward : float               the -wirelength-congestion or zeros
        done : bool           whether the game end or not
        info : {'valid' : np.array}    a dict shows the valid place for the next player
        """
        if (len(np.nonzero(self.board)[0]) >= self.T):
            action = self.illegal_equivalent_action
        if np.array_equal(action, self.RESIGN):
            reward = self.get_reward(state)
            return state, reward, True, {}
        while True:
            state = self.get_next_state(state, action)
            return state, 0., False, {}

    def step(self,action):
        state = (self.board, self.device)
        next_state, reward, done, info = self.next_step(state, action)
        self.board, self.device = next_state
        return next_state, reward, done, info
   
    #显示
    def render(self, mode='human'):
        """
        See gym.Env.render().
        """
        outfile = StringIO() if mode == 'ansi' else sys.stdout
        s = strfboard(self.board, self.render_characters)
        outfile.write(s)
        if mode != 'human':
            return outfile





