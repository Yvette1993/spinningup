import yaml
import os

class LoadData(object):
    def __init__(self, path):
        yaml_path = path
        file = open(yaml_path, 'r', encoding='utf-8')
        content = file.read()
        data = yaml.load(content, Loader=yaml.FullLoader)
        self.data = data

## test
# root = os.getcwd()
# file_path = os.path.join(root, 'spinningup/envs/chip_place_gym/envs/test.yaml')
# data = LoadData(file_path)
# print(type(data))
# print(data)
# print(data.data)
# print(data.data['Nodes'][1]['adj'])