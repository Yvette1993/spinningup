import sys
import os
sys.path.append('/home/lisali/spinningup/envs')
root = os.getcwd()
file_path = os.path.join(root, 'spinningup/envs/chip_place_gym/envs/test.yaml')

from gym.envs.classic_control import rendering
import gym
from chip_place_gym.envs import geom
from load_data import *

class acp_sandbox(object):
    def __init__(self):
        data = LoadData(file_path)







class ChipPlaceEnv(gym.Env):
    metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second': 1
    }

    def __init__(self):
        self.sandbox = acp_sandbox()
        self.resolution = (900, 900)
        self.viewer = rendering.Viewer(*self.resolution)
        print('CellPlaceEnv Environment initialized')

    def reset(self):  ## init env
        print('CellPlaceEnv Environment reset')

    def step(self):
        # print('CellPlaceEnv Step successful!')
        return self.sandbox.step()

    def render(self, mode='human', close=False):
        # # 下面就可以定义你要绘画的元素了
        # line1 = rendering.Line((100, 300), (500, 300))
        # line2 = rendering.Line((100, 200), (500, 200))
        # # 给元素添加颜色
        # line1.set_color(0, 0, 0)
        # line2.set_color(0, 0, 0)
        # # 把图形元素添加到画板中
        # self.viewer.add_geom(line1)
        # self.viewer.add_geom(line2)

        self.draw_placement(self.sandbox.place)

        return self.viewer.render(return_rgb_array=mode == 'rgb_array')

    def draw_placement(self, p):
        # Draw grid
        cw, ch = self.canvas_size
        rw, rh = self.resolution

        grid_size_w = rw // cw
        grid_size_h = rh // ch

        grid_remain_w = rw % cw
        grid_remain_h = rh % ch

        max_circle_radius = min(grid_size_w, grid_size_h) // 3

        for wi in range(0, rw, grid_size_w):
            self.draw_line((wi, 0), (wi, rh))

        for hi in range(0, rh, grid_size_h):
            self.draw_line((0, hi), (rw, hi))

        for port in self.design_ports:
            if port.cell_position:
                pw = port.cell_position['x'] * grid_size_w + grid_size_w // 2
                ph = port.cell_position['y'] * grid_size_h + grid_size_h // 2
                self.draw_circle(pw, ph, radius=max_circle_radius, )

        for cell in self.design_cells:
            if cell.cell_position:
                pw = cell.cell_position['x'] * grid_size_w + grid_size_w // 2
                ph = cell.cell_position['y'] * grid_size_h + grid_size_h // 2
                self.draw_circle(pw, ph, radius=max_circle_radius, color=(.5, .5, 1))

        # Draw edges
        for net in self.design_nets:
            from_p = net.net_source.get_position()
            if not from_p:
                continue
            from_x = from_p['x'] * grid_size_w + grid_size_w // 2
            from_y = from_p['y'] * grid_size_h + grid_size_h // 2
            for dest in net.net_dests:

                to_p = dest.get_position()
                if not to_p:
                    continue
                to_x = to_p['x'] * grid_size_w + grid_size_w // 2
                to_y = to_p['y'] * grid_size_h + grid_size_h // 2

                self.draw_line((from_x, from_y), (to_x, to_y), thickness=10, color=(.1, .8, .5))

    def draw_line(self, x1, x2, thickness=1, color=(0, 0, 0)):
        line = geom.Line(x1, x2, thickness)
        line.set_color(*color)
        self.viewer.add_geom(line)

    def draw_circle(self, x, y, radius=10, color=(1, .5, .5)):
        circle = rendering.make_circle(radius)
        circle.set_color(*color)
        circle.add_attr(rendering.Transform(translation=(x, y)))
        self.viewer.add_geom(circle)

    def draw_rectangle(self, x, y, width, height, color=(1, 0, 0)):
        l = (x - width / 2)
        r = -(x + width / 2)
        t = (y + height / 2)
        b = -(x - width / 2)
        rect = rendering.FilledPolygon([(l, b), (l ,t), (r, t), (r, b)])
        rect.set_color(*color)
        rect.add_attr(rendering.Transform(translation=(x,y)))
        self.viewer.add_geom(rect)

    def close(self):
        self.viewer.close()

    @property
    def canvas_size(self):
        return self.sandbox.place.canvas.width, self.sandbox.place.canvas.height

    @property
    def design_ports(self):
        return self.sandbox.design.ports

    @property
    def design_cells(self):
        return self.sandbox.design.cells

    @property
    def design_nets(self):
        return self.sandbox.design.nets