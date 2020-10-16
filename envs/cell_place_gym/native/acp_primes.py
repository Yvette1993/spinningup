
class acp_prime_port (object):

    def __init__ (self):
        self.port_id           = {'name':'_port_', 'id':-1}
        self.port_type         = 'chip'
        self.port_status       = 'open'
        self.port_dir          = 'input'
        self.port_attr         = 'data_flow'
        self.port_width        = 8
        self.port_net          = None
        self.cell_type         = 'port'
        # Position can be when type == chip => {'x':1, 'y':1, 'design':...} or {'cell':_cell_it_connected_} 
        self.port_position     = {}
        self.cell_position     = {}

    def __repr__ (self):
        if self.port_type == 'chip':
            l_str = '%s.%s' % (self.port_position['design'].name, self.port_id['name'])
            return l_str
        else:
            l_str = '%s.%s' % (self.port_position['cell'].cell_name(), self.port_id['name'])
            return l_str

    def spawn (self):
        l_inst = acp_prime_port ()
        l_inst.port_id['name'] = self.port_id['name']
        l_inst.port_id['id'  ] = self.port_id['id'  ]
        l_inst.port_type       = self.port_type
        l_inst.port_dir        = self.port_dir
        l_inst.port_attr       = self.port_attr
        l_inst.port_width      = self.port_width
        return l_inst

    def get_inst_id (self):
        l_ret = -1
        if self.port_type == 'chip':
            l_ret = self.port_id['inst_id']
        else:
            cell  = self.port_position['cell']
            l_ret = cell.cell_id['inst_id']
        return l_ret

    def get_position (self):
        l_ret = {}
        if self.port_type == 'chip':
            cell = self
        else:
            cell = self.port_position['cell']
        if 'x' in cell.cell_position:
            l_ret['x'] = cell.cell_position['x']
            l_ret['y'] = cell.cell_position['y']
        return l_ret

    def is_placed (self):
        l_ret = False
        if self.port_type == 'chip':
            if 'x' in self.port_position:
                l_ret = True
        else:
            cell = self.port_position['cell']
            if 'x' in cell.cell_position:
                l_ret = True
        return l_ret

class acp_prime_cell (object):

    def __init__ (self, cell_type = 'unknown'):
        self.cell_id           = {'name':'_cell_', 'id':-1}
        self.cell_type         = cell_type
        self.cell_status       = 'created'
        # Position is {'x':1, 'y':1} which is position on grid 
        self.cell_position     = {}
        self.cell_ports        = {'input':[], 'output':[]}
        self.cell_port_map     = {}     

    def cell_name (self):
        if self.cell_id['name'] == '_cell_':
            return '%s_%s' % (self.cell_type, self.cell_id['id'])
        else:
            return self.cell_id['name']

    def __repr__ (self):
        l_str = '- cell %s of %s' % (self.cell_name(), self.cell_type)
        return l_str

    def add_port (self, name, dir, width = 8):
        l_port = acp_prime_port ()
        self.cell_ports[dir].append (l_port)
        self.cell_port_map[name] = l_port
        l_port.port_id['name']   = name
        l_port.port_id['id'  ]   = len (self.cell_ports[dir])
        l_port.port_position     = {'cell':self}
        l_port.port_width        = 8
        l_port.port_type         = 'cell'
        l_port.port_dir          = dir
        return l_port

    def add_port_quick (self, l_port):
        name = l_port.port_id['name']
        dir  = l_port.port_dir
        self.cell_ports[dir].append (l_port)
        self.cell_port_map[name] = l_port
        l_port.port_position     = {'cell':self}
        return l_port

    def spawn (self):
        l_inst = acp_prime_cell ()
        l_inst.cell_type  = self.cell_type
        for p in self.cell_ports['input']:
            l_p = p.spawn ()
            l_inst.add_port_quick (l_p)
        for p in self.cell_ports['output']:
            l_p = p.spawn ()
            l_inst.add_port_quick (l_p)
        return l_inst

    def get_position (self):
        l_ret = {}
        if self.is_placed():
            l_ret['x'] = self.cell_position['x']
            l_ret['y'] = self.cell_position['y']
        return l_ret

    def is_placed (self):
        l_ret = False
        if 'x' in self.cell_position:
            l_ret = True
        return l_ret

class acp_prime_net (object):

    def __init__ (self):
        self.net_id            = {'name':'_net_', 'id':-1}
        self.net_weight        = 1
        self.net_type          = 'data_flow'
        self.net_status        = 'floating'
        self.net_source        = None
        self.net_dests         = []

    def __repr__ (self):
        l_str = '- net  %s' % self.net_id['name']
        return l_str

    def connection_str (self):
        conn_str = ''
        if self.net_source:
            conn_str += '%s -> ' % self.net_source
        for dst in self.net_dests:
            if dst == self.net_dests[-1]:
                conn_str += '%s'    % dst
            else:
                conn_str += '%s, '  % dst
        hpwl = self.get_net_length ()
        if hpwl is not None:
            conn_str += ' (length: %s)'  % hpwl
        return conn_str

    def get_net_length (self, mode = 'HPWL'):
        if self.net_status != 'placed' or not self.net_source or len (self.net_dests) == 0:
            return None
        l_x     = []
        l_y     = []
        l_cells = []
        if 'design' in self.net_source.port_position:
            l_cells.append (self.net_source)
        else:
            l_cells.append (self.net_source.port_position['cell'])
        for port in self.net_dests:
            if 'design' in port.port_position:
                l_cells.append (port)
            else:
                l_cells.append (port.port_position['cell'])
        for cell in l_cells:
            l_x.append (cell.cell_position['x'])
            l_y.append (cell.cell_position['y'])
        min_x = min (l_x)
        max_x = max (l_x)
        min_y = min (l_y)
        max_y = max (l_y)
        hpwl  = max_x - min_x + max_y - min_y
        return hpwl

class acp_design (object):

    def __init__ (self, name = 'top_design'):
        self.name              = name
        self.cell_map          = {}
        self.port_map          = {}
        self.ports             = []
        self.cells             = []
        self.nets              = []
        self.instances         = []

    def __repr__ (self):
        l_str_list  = '<design %s>\n' % self.name
        l_str_list += '+ nets\n'
        for net in self.nets:
            l_str = '%s\n' % net
            l_str_list += l_str
        l_str_list += '+ cells\n'
        for cell in self.cells:
            l_str = '%s\n' % cell
            l_str_list += l_str
        l_str_list += '</design %s>' % self.name
        return l_str_list

    def new_inst (self, inst):
        if hasattr (inst, 'port_id'):
            inst.port_id['inst_id'] = len (self.instances)
        else:
            inst.cell_id['inst_id'] = len (self.instances)
        self.instances.append (inst)
        return

    # define ports on top level design
    def def_port (self, name, dir, width = 8):
        l_port = acp_prime_port ()
        self.ports.append (l_port)
        self.port_map[name] = l_port
        l_port.port_id['name']         = name
        l_port.port_id['id'  ]         = len (self.ports)
        l_port.port_dir                = dir
        l_port.port_width              = width
        l_port.port_position['design'] = self
        self.new_inst (l_port)
        return l_port

    def add_cell (self, cell):
        cell.cell_id['id'] = len (self.cells)
        self.cells.append (cell)
        self.cell_map[cell.cell_id['name']] = cell.cell_id['id']
        self.new_inst (cell)
        return cell

    def connection_sanity_check (self, from_port, to_port):
        if (from_port.port_dir == 'input'  and to_port.port_dir == 'output') or (from_port.port_dir == 'output' and to_port.port_dir == 'input'):
            if from_port.port_type == 'cell' and to_port.port_type == 'cell':
                if from_port.port_attr == to_port.port_attr:
                    return 'cell'
        if from_port.port_dir == to_port.port_dir:
            if (from_port.port_type == 'chip' and to_port.port_type != 'chip') or (from_port.port_type != 'chip' and to_port.port_type == 'chip'):
                if from_port.port_attr == to_port.port_attr:
                    return 'design'
        return 'fail'                    

    def connect_ports (self, from_port, to_port):
        # sanity check
        if self.connection_sanity_check (from_port, to_port) == 'fail':
            # please check the connection
            print ('connect_ports error')
            return None
        # do the connection
        if from_port.port_net:
            l_net = from_port.port_net
            if to_port.port_net and to_port.port_net != l_net:
                raise Exception ('Trying to make illegal connection')
            l_net.net_dests.append (to_port)
            to_port.port_net    = l_net
            to_port.port_status = 'connected'
        elif to_port.port_net:
            l_net = to_port.port_net
            if l_net.net_source and l_net.net_source != from_port:
                raise Exception ('Trying to make multi-driven connection')
            l_net.net_source      = from_port
            from_port.port_net    = l_net
            from_port.port_status = 'connected'
        else:
            l_net = acp_prime_net ()
            self.nets.append (l_net)
            l_net.net_id ['id'  ] = len (self.nets)
            l_net.net_id ['name'] = 'net_%d_from_%s_to_%s' % (l_net.net_id ['id'], from_port.port_id['name'], to_port.port_id['name']) 
            l_net.net_source      = from_port
            to_port.port_status   = 'connected'
            from_port.port_status = 'connected'
            l_net.net_dests.append (to_port)
        # assign net weight
        l_net.net_weight = from_port.port_width
        l_net.net_type   = from_port.port_type
        l_net.net_status = 'connected' 
        return l_net

    def check_place (self):
        placed = True
        for port in self.ports:
            if port.cell_status != 'placed':
                placed = False
                break
        for cell in self.cells:
            if cell.cell_status != 'placed':
                placed = False
                break
        if placed:
            for net in self.nets:
                net.net_status = 'placed'
        return placed

    def get_nets_length (self, mode = 'HPWL'):
        length = 0.0
        for net in self.nets:
            l = net.get_net_length (mode)
            if l is not None:
                length += l
            else:
                print ('net has no length : %s' % net)
        return length

    def print_connections (self):
        print ('<design connetions %s>' % self.name)
        for net in self.nets:
            l_str = net.connection_str ()
            print ('- ' + l_str)
        print ('</design connetions %s>' % self.name)

if __name__ == '__main__':

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

    my_design.print_connections ()
