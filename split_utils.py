# -*- coding: utf-8 -*-

import os, sys
import numpy as np
import itertools

def get_splitting_coors(wsi_w, wsi_h, block_size):
    def split_coor(ttl_len, sub_len):
        split_num = int(np.floor((ttl_len + sub_len / 2) / sub_len))
        split_pair = [(num * sub_len, sub_len) for num in range(split_num-1)]
        split_pair.append(((split_num-1) * sub_len, ttl_len - (split_num-1) * sub_len))
        return split_pair

    w_pairs = split_coor(wsi_w, block_size)
    h_pairs = split_coor(wsi_h, block_size)
    coors_list = [(ele[0][0], ele[1][0], ele[0][1], ele[1][1]) for ele in list(itertools.product(w_pairs, h_pairs))]

    return coors_list
