# -*- coding: utf-8 -*-

import os, sys
import shutil, argparse, pytz
from datetime import datetime
import openslide
import math, json
import numpy as np

from misc.utils import shift_contour


def set_args():
    parser = argparse.ArgumentParser(description = "Merge Block Segmentations")
    parser.add_argument("--data_root",         type=str,       default="/Data")
    parser.add_argument("--block_seg_dir",     type=str,       default="BlockSegs")
    parser.add_argument("--slide_seg_dir",     type=str,       default="SlideSegs")
    parser.add_argument("--dataset",           type=str,       default="URMC", choices=["URMC", "MDACC", "UNMC"])    

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = set_args()
    # Slide directory
    data_root = os.path.join(args.data_root, args.dataset)
    block_seg_root_dir = os.path.join(data_root, args.block_seg_dir)
    slide_seg_root_dir = os.path.join(data_root, args.slide_seg_dir)
    if not os.path.exists(slide_seg_root_dir):
        os.makedirs(slide_seg_root_dir)

    # process slide one-by-one
    slide_list = sorted([ele for ele in os.listdir(block_seg_root_dir) if os.path.isdir(os.path.join(block_seg_root_dir, ele))])
    for idx, cur_slide in enumerate(slide_list):
        cur_time_str = datetime.now(pytz.timezone('America/Chicago')).strftime("%H:%M:%S")
        print("@ {} Start merging {:2d}/{:2d} {}".format(cur_time_str, idx+1, len(slide_list), cur_slide))
        # combine block's segmentation
        slide_nuc_dict = {}
        slide_nuc_id = 1
        block_seg_dir = os.path.join(block_seg_root_dir, cur_slide)
        block_list = sorted([os.path.splitext(ele)[0] for ele in os.listdir(block_seg_dir) if ele.endswith(".json")])
        for block_idx, cur_block in enumerate(block_list):
            print("...Analyze {:3d}/{:3d} {}".format(block_idx+1, len(block_list), cur_block))
            wstart_pos = cur_block.index("Wstart")
            hstart_pos = cur_block.index("Hstart")
            wlen_pos = cur_block.index("Wlen")
            hlen_pos = cur_block.index("Hlen")
            block_wstart = int(cur_block[wstart_pos+len("Wstart"):hstart_pos])
            block_hstart = int(cur_block[hstart_pos+len("Hstart"):wlen_pos])
            block_width = int(cur_block[wlen_pos+len("Wlen"):hlen_pos])
            block_height = int(cur_block[hlen_pos+len("Hlen"):len(cur_block)])
            # read segmentation
            cur_seg_path = os.path.join(block_seg_dir, cur_block + ".json")
            seg_inst_dict = json.load(open(cur_seg_path, "r"))
            nuc_dict = seg_inst_dict["nuc"]
            # traverse nucleus one-by-one
            for ind, cur_inst in enumerate(nuc_dict.keys()):
                slide_nuc_dict[str(slide_nuc_id)] = shift_contour(nuc_dict[cur_inst], block_wstart, block_hstart)
                slide_nuc_id += 1
        # save json file
        slide_json_path = os.path.join(slide_seg_root_dir, cur_slide + ".json")
        with open(slide_json_path, 'w') as fp:
            json.dump(slide_nuc_dict, fp)
