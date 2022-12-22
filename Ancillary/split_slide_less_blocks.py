# -*- coding: utf-8 -*-

import os, sys
import copy, argparse, pytz
from datetime import datetime
import shutil


def set_args():
    parser = argparse.ArgumentParser(description = "Splitting WSI to blocks")
    parser.add_argument("--data_root",         type=str,       default="/Data")
    parser.add_argument("--split_num",         type=int,       default=4)

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = set_args()
    # directory
    block_src_dir = os.path.join(args.data_root, "SlideBlocks")
    block_dst_dir = os.path.join(args.data_root, "SlideBlocks" + str(args.split_num))
    if os.path.exists(block_dst_dir):
        shutil.rmtree(block_dst_dir)
    os.makedirs(block_dst_dir)
    # start the copying process
    slide_list = sorted([ele for ele in os.listdir(block_src_dir) if os.path.isdir(os.path.join(block_src_dir, ele))])
    for ind, cur_slide in enumerate(slide_list):
        print("split {}/{}".format(ind+1, len(slide_list)))
        block_num = len([ele for ele in os.listdir(os.path.join(block_src_dir, cur_slide)) if ele.endswith(".png")])
        src_block_dir = os.path.join(block_src_dir, cur_slide)
        if block_num <= args.split_num:
            dst_block_dir = os.path.join(block_dst_dir, cur_slide)
            shutil.move(src_block_dir, dst_block_dir)
