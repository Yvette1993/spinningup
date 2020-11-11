#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Time: 2020/10/30 10:21:06
# Author: Yingying Li

# 应用归简法求解拓扑排序，计算拓扑结构中每个节点的入度，移除入度为0的节点，（入度为 0 表没有任何节点指向它），
#然后再判断解决剩下的节点

def topological_sort(graph):
    in_degrees = dict((u, 0) for u in graph)
    for u in graph:#遍历键值
        for v in graph[u]:  # 根据键找出值也就是下级节点
            in_degrees[v] += 1  # 对获取到的下级节点的入度加 1

    # 循环结束之后的结果: {'a': 0, 'b': 1, 'c': 1, 'd': 2, 'e': 1, 'f': 4}
    Q = [u for u in graph if in_degrees[u] == 0]  # 找出入度为 0 的节点
    in_degrees_zero = []
    while Q:
        u = Q.pop()  # 默认从最后一个移除
        in_degrees_zero.append(u)  # 存储入度为 0 的节点
        for v in graph[u]:
            in_degrees[v] -= 1  # 删除入度为 0 的节点，以及移除其指向
            if in_degrees[v] == 0:
                Q.append(v)
    return in_degrees_zero

if __name__ == '__main__':

    
    # 用字典的键值表示图的节点之间的关系，键为所有顶点。值是该顶点指向的顶点。
    graph_dict = {
        'a': 'bf',  # 表示 a 指向 b 和 f
        'b': 'cdf',
        'c': 'd',
        'd': 'ef',
        'e': 'f',
        'f': ''
    }

    t = topological_sort(graph_dict)
    print(t)