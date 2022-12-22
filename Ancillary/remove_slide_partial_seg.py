# -*- coding: utf-8 -*-

import os, sys
import shutil, argparse, pytz
from datetime import datetime
import numpy as np
from skimage import io


def set_args():
    parser = argparse.ArgumentParser(description = "Splitting WSI to blocks")
    parser.add_argument("--data_root",         type=str,       default="/Data")
    parser.add_argument("--block_dir",         type=str,       default="SlideBlocks")
    parser.add_argument("--seg_dir",           type=str,       default="BlockSegs")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = set_args()
    # Slide directory
    slide_block_dir = os.path.join(args.data_root, args.block_dir)
    block_done_dir = os.path.join(args.data_root, args.block_dir + "Done")
    slide_seg_dir = os.path.join(args.data_root, args.seg_dir)

    slide_list = [ele for ele in os.listdir(slide_block_dir) if os.path.isdir(os.path.join(slide_block_dir, ele))]
    for cur_slide in slide_list:
        cur_slide_block_dir = os.path.join(slide_block_dir, cur_slide)
        cur_slide_seg_dir = os.path.join(slide_seg_dir, cur_slide)
        if not os.path.exists(cur_slide_seg_dir):
            continue

        block_num = len([ele for ele in os.listdir(cur_slide_block_dir) if ele.endswith(".png")])
        seg_num = len([ele for ele in os.listdir(cur_slide_seg_dir) if ele.endswith(".json")])
        if block_num != seg_num:
            shutil.rmtree(cur_slide_seg_dir)
        else:
            shutil.move(cur_slide_block_dir, block_done_dir)



