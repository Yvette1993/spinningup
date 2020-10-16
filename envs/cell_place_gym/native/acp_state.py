import numpy as np

from cell_place_gym.native.acp_placement import *

class acp_placement_state (object):

    def __init__ (self, place):
        self.place    = place
        self.design   = place.design
        l_inst_count  = len (self.design.instances)
        # Non-Placed Nets Matrix
        self.c_matrix = np.zeros (shape = (l_inst_count, l_inst_count))
        # Placed Nets Matrix
        self.n_matrix = np.zeros (shape = (l_inst_count, l_inst_count))

    def get_state (self):
        nets = self.design.nets
        self.c_matrix [:,:] = 0
        self.n_matrix [:,:] = 0
        for n in nets:
            src          = n.net_source
            src_id       = src.get_inst_id ()
            src_placed   = src.is_placed ()
            src_position = src.get_position ()
            for dst in n.net_dests:
                dst_id       = dst.get_inst_id ()
                dst_placed   = dst.is_placed ()
                dst_position = dst.get_position ()
                if src_placed and dst_placed:
                    self.n_matrix [src_id][dst_id] = 1
                else:
                    self.n_matrix [src_id][dst_id] = 1
        return
