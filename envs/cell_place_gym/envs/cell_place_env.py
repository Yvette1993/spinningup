import gym
from cell_place_gym.envs import geom
from gym.envs.classic_control import rendering

from cell_place_gym.native.acp_primes    import *
from cell_place_gym.native.acp_placement import *
from cell_place_gym.native.acp_state     import *

from gym.envs.classic_control.rendering import make_circle, LineWidth

class acp_sandbox(object):

    def __init__(self):
        # define design

        my_design = acp_design()
        my_design.def_port('data_inp_0', 'input')
        my_design.def_port('data_inp_1', 'input')
        my_design.def_port('data_inp_2', 'input')
        my_design.def_port('data_inp_3', 'input')
        my_design.def_port('data_out_0', 'output')

        # define cells

        dsp_inst_0 = acp_prime_cell('dsp')
        dsp_inst_0.add_port('src0', 'input')
        dsp_inst_0.add_port('src1', 'input')
        dsp_inst_0.add_port('dest', 'output')

        dsp_inst_1 = dsp_inst_0.spawn()
        dsp_inst_2 = dsp_inst_0.spawn()

        # add cells

        my_design.add_cell(dsp_inst_0)
        my_design.add_cell(dsp_inst_1)
        my_design.add_cell(dsp_inst_2)

        # connect cells
        my_design.connect_ports(my_design.port_map['data_inp_0'], dsp_inst_0.cell_port_map['src0'])
        my_design.connect_ports(my_design.port_map['data_inp_1'], dsp_inst_0.cell_port_map['src1'])

        my_design.connect_ports(my_design.port_map['data_inp_2'], dsp_inst_1.cell_port_map['src0'])
        my_design.connect_ports(my_design.port_map['data_inp_3'], dsp_inst_1.cell_port_map['src1'])

        my_design.connect_ports(dsp_inst_0.cell_port_map['dest'], dsp_inst_2.cell_port_map['src0'])
        my_design.connect_ports(dsp_inst_1.cell_port_map['dest'], dsp_inst_2.cell_port_map['src1'])

        my_design.connect_ports(dsp_inst_2.cell_port_map['dest'], my_design.port_map['data_out_0'])

        print(my_design)

        place = acp_placement(5, 5)
        place.canvas.add_device_budget('dsp', 1)
        place.canvas.finalize_io()

        place.set_design(my_design, 'rand')

        # place io
        place.canvas.place_cell(my_design.ports[0], 0, 0)
        place.canvas.place_cell(my_design.ports[1], 1, 0)
        place.canvas.place_cell(my_design.ports[2], 2, 0)
        place.canvas.place_cell(my_design.ports[3], 3, 0)
        place.canvas.place_cell(my_design.ports[4], 0, 4)

        # end of design

        self.design = my_design
        self.place  = place
        self.state  = acp_placement_state (self.place)

    def step(self):
        # place one cell by using random strategy
        success = self.place.place_cell()
        # check end of place
        done = self.design.check_place()
        # state
        self.state.get_state ()
        # return
        return (success, done)


class CellPlaceEnv(gym.Env):
    metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second': 1
    }

    def __init__(self):
        self.sandbox = acp_sandbox()
        self.resolution = (600, 400)
        self.viewer = rendering.Viewer(*self.resolution)
        print('CellPlaceEnv Environment initialized')

    def reset(self):
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

    def draw_rectangle(self, x1, y1, x2, y2, color=(1, 0, 0)):
        rect = geom.Rectangle()

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
