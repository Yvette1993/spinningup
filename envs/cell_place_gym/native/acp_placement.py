import numpy as np

from random     import randint

class acp_placement_canvas (object):

    def __init__ (self, width, height):
        self.width  = width
        self.height = height
        self.grids  = {}
        self.placed = {}
        self.budget = {}
        self.device_info = {'budget':{}}

    def add_device_budget (self, device_type, budget = 1):
        l_grid = np.full (shape = (self.height, self.width), fill_value = budget)
        self.grids [device_type] = l_grid
        self.placed[device_type] = []
        self.budget[device_type] = (self.height - 2) * (self.width - 2) * budget
        self.device_info['budget'][device_type] = budget
        # clear IO ring grids
        limit = self.width
        for i in range (limit):
            l_grid[        0][i] = 0
            l_grid[limit - 1][i] = 0
        limit = self.height
        for i in range (limit):
            l_grid[i][        0] = 0
            l_grid[i][limit - 1] = 0
        return l_grid

    def finalize_io (self):
        device_type = 'port'
        l_grid      = np.full (shape = (self.height, self.width), fill_value = 0)
        self.grids [device_type] = l_grid
        self.placed[device_type] = []
        self.budget[device_type] = self.height * 2 + (self.width - 2) * 2
        # finalize IO ring grids
        limit = self.width
        for i in range (limit):
            l_grid[        0][i] = 1
            l_grid[limit - 1][i] = 1
        limit = self.height
        for i in range (limit):
            l_grid[i][        0] = 1
            l_grid[i][limit - 1] = 1
        return l_grid

    def can_place_at (self, cell, x, y):
        cell_type = cell.cell_type
        if cell_type in self.grids:
            cell_grid = self.grids [cell_type]
            if cell_grid[y][x] > 0:
                return True
        return False

    def place_cell (self, cell, x, y):
        cell_type = cell.cell_type
        if cell_type in self.grids:
            cell_grid = self.grids [cell_type]
            if cell_grid[y][x] > 0:
                cell_grid[y][x] -= 1
                self.placed [cell_type].append (cell)
                self.budget [cell_type] -= 1
                cell.cell_status         = 'placed'
                cell.cell_position['x']  = x
                cell.cell_position['y']  = y
            return True
        # invalid place
        return False

class acp_placement_strategy (object):

    def __init__ (self, canvas):
        self.canvas = canvas

    def find_place_for_cell (self, cell, strategy = 'seq'):
        if strategy == 'seq':
            for y in range (1, self.canvas.height - 1, 1):
                for x in range (1, self.canvas.width - 1, 1):
                    if self.canvas.can_place_at (cell, x, y):
                        return (x, y)
            return (None, None)
        if strategy == 'rand':
            for _ in range (5):
                y = randint (1, self.canvas.height - 2)
                x = randint (1, self.canvas.width  - 2)
                if self.canvas.can_place_at (cell, x, y):
                    return (x, y)
            return self.find_place_for_cell(cell)

class acp_placement (object):

    def __init__ (self, width, height):
        self.canvas = acp_placement_canvas (width, height)
        self.placer = acp_placement_strategy (self.canvas)

    def set_design (self, design, place_strategy = 'seq'):
        self.design         = design
        self.place_strategy = place_strategy
        self.place_index    = 0
        self.place_hpwl     = 0.0         
        return

    def place_cell (self):
        if self.place_index < len (self.design.cells):
            l_cell            = self.design.cells[self.place_index]
            self.place_index += 1
            pos_x, pos_y      = self.placer.find_place_for_cell (l_cell, self.place_strategy)
            if pos_x and pos_y:
                self.canvas.place_cell (l_cell, pos_x, pos_y)    
                return True
        return False

    def do_place (self):
        while True:
            success = self.place_cell ()
            if not success:
                break
        return

if __name__ == '__main__':

    from acp_primes import *
    
    my_design = acp_design ()
    my_design.def_port ('data_inp_0', 'input')
    my_design.def_port ('data_inp_1', 'input')
    my_design.def_port ('data_inp_2', 'input')
    my_design.def_port ('data_inp_3', 'input')
    my_design.def_port ('data_out_0', 'output')
    
    # define cells
    
    dsp_inst_0 = acp_prime_cell ('dsp')
    dsp_inst_0.add_port ('src0', 'input')
    dsp_inst_0.add_port ('src1', 'input')
    dsp_inst_0.add_port ('dest', 'output')
    
    dsp_inst_1 = dsp_inst_0.spawn ()
    dsp_inst_2 = dsp_inst_0.spawn ()

    # add cells

    my_design.add_cell (dsp_inst_0)
    my_design.add_cell (dsp_inst_1)
    my_design.add_cell (dsp_inst_2)

    # connect cells
    my_design.connect_ports (my_design.port_map['data_inp_0'], dsp_inst_0.cell_port_map['src0'])
    my_design.connect_ports (my_design.port_map['data_inp_1'], dsp_inst_0.cell_port_map['src1'])

    my_design.connect_ports (my_design.port_map['data_inp_2'], dsp_inst_1.cell_port_map['src0'])
    my_design.connect_ports (my_design.port_map['data_inp_3'], dsp_inst_1.cell_port_map['src1'])
    
    my_design.connect_ports (dsp_inst_0.cell_port_map['dest'], dsp_inst_2.cell_port_map['src0'])
    my_design.connect_ports (dsp_inst_1.cell_port_map['dest'], dsp_inst_2.cell_port_map['src1'])

    my_design.connect_ports (dsp_inst_2.cell_port_map['dest'], my_design.port_map['data_out_0'])

    print (my_design)

    place = acp_placement (5, 5)
    place.canvas.add_device_budget ('dsp', 1)
    place.canvas.finalize_io ()

    place.set_design (my_design, 'seq')

    place.canvas.place_cell (my_design.ports[0], 0, 0)
    place.canvas.place_cell (my_design.ports[1], 1, 0)
    place.canvas.place_cell (my_design.ports[2], 2, 0)
    place.canvas.place_cell (my_design.ports[3], 3, 0)
    place.canvas.place_cell (my_design.ports[4], 0, 4)
    place.do_place ()

    my_design.check_place ()
    my_design.print_connections ()
    
    hpwl = my_design.get_nets_length ()
    print ('HPWL : %s' % hpwl)
