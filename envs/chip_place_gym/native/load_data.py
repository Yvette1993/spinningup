#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Time: 2020/11/05 17:35:42
# Author: Yingying Li
import yaml
import os
import collections
import numpy as np

class LoadData(object):
    def __init__(self, path):
        yaml_path = path
        file = open(yaml_path, 'r', encoding='utf-8')
        content = file.read()
        data = yaml.load(content, Loader=yaml.FullLoader)
        self.data = data

    def parser_yaml(self):
        nodes = self.data
        graph_dict = collections.OrderedDict()
        for node in nodes['Nodes']:
            key = str(node['id'])
            adj = np.nonzero(node['adj'])[0]
            value = [i for i in adj]
            graph_dict[key] = value
            node['adj'] = value        # 
        return graph_dict, nodes['Nodes']
    
    # 应用归简法求解拓扑排序，计算拓扑结构中每个节点的入度，移除入度为0的节点，（入度为 0 表没有任何节点指向它），
    #然后再判断解决剩下的节点

    def topological_sort(self,graph):
        in_degrees = dict((u, 0) for u in graph)
        for u in graph:#遍历键值
            for v in graph[u]:  # 根据键找出值也就是下级节点
                in_degrees[str(v)] += 1  # 对获取到的下级节点的入度加 1

        # 循环结束之后的结果:['4', '3', '5', '1', '0', '2', '6']
        Q = [u for u in graph if in_degrees[u] == 0]  # 找出入度为 0 的节点
        in_degrees_zero = []
        while Q:
            u = Q.pop()  # 默认从最后一个移除
            in_degrees_zero.append(u)  # 存储入度为 0 的节点
            for v in graph[u]:
                in_degrees[str(v)] -= 1  # 删除入度为 0 的节点，以及移除其指向
                if in_degrees[str(v)] == 0:
                    Q.append(str(v))
        return in_degrees_zero

    def get_DAG_data(self):
        graph_dict, nodes_data = self.parser_yaml()
        Data =[]
        DAG = self.topological_sort(graph_dict)
        for i in DAG:
            for node in nodes_data:
                if node['id'] == int(i):
                    Data.append(node)
        return  Data

## test
root = os.getcwd()
file_path = os.path.join(root, 'test.yaml')
# file_path = os.path.join(root, 'envs/chip_place_gym/envs/test.yaml')
data = LoadData(file_path)
Data  = LoadData.get_DAG_data(data)

print(Data)
