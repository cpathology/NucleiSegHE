# -*- coding: utf-8 -*-

import os, sys
import copy, argparse, pytz
from datetime import datetime


def set_args():
    parser = argparse.ArgumentParser(description = "Splitting WSI to blocks")
    parser.add_argument("--data_root",         type=str,       default="/Data")
    parser.add_argument("--block_dir",         type=str,       default="SlideBlocks")
    parser.add_argument("--seg_dir",           type=str,       default="BlockSegs")

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = set_args()

    slide_block_dir = os.path.join(args.data_root, args.block_dir)
    block_seg_dir = os.path.join(args.data_root, args.seg_dir)
    slide_list = sorted([ele for ele in os.listdir(slide_block_dir) if os.path.isdir(os.path.join(slide_block_dir, ele))])
    for cur_slide in slide_list:
        block_num = len([ele for ele in os.listdir(os.path.join(slide_block_dir, cur_slide)) if ele.endswith(".png")])
        seg_num = len([ele for ele in os.listdir(os.path.join(block_seg_dir, cur_slide)) if ele.endswith(".json")])
        if block_num != seg_num:
            print("{} complete {}/{}".format(cur_slide, seg_num, block_num))
