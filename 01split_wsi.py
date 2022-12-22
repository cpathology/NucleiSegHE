# -*- coding: utf-8 -*-

import os, sys
import shutil, argparse, pytz
from joblib import Parallel, delayed
from datetime import datetime
import openslide
import numpy as np
from skimage import io

from split_utils import get_splitting_coors


def set_args():
    parser = argparse.ArgumentParser(description = "Splitting WSI to blocks")
    parser.add_argument("--data_root",         type=str,       default="/Data")
    parser.add_argument("--slide_dir",         type=str,       default="RawSlides")
    parser.add_argument("--block_dir",         type=str,       default="SlideBlocks")
    parser.add_argument("--block_size",        type=int,       default=8000)
    parser.add_argument("--num_workers",       type=int,       default=64)
    parser.add_argument("--dataset",           type=str,       default="URMC", choices=["URMC", "MDACC", "UNMC"])    
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = set_args()
    # Slide directory
    slide_root_dir = os.path.join(args.data_root, args.dataset, args.slide_dir)
    slide_list = sorted([ele for ele in os.listdir(slide_root_dir) if os.path.splitext(ele)[1] in [".svs", ".tiff", ".tif"]])
    # Block directory
    block_root_dir = os.path.join(args.data_root, args.dataset, args.block_dir)
    if not os.path.exists(block_root_dir):
        os.makedirs(block_root_dir)

    # split slides one-by-one
    for idx, cur_slide in enumerate(slide_list):
        cur_time_str = datetime.now(pytz.timezone('America/Chicago')).strftime("%m/%d/%Y, %H:%M:%S")
        print("Start @ {}".format(cur_time_str))
        cur_slide_name = os.path.splitext(cur_slide)[0]
        # prepare block directory
        slide_block_dir = os.path.join(block_root_dir, cur_slide_name)
        if not os.path.exists(slide_block_dir):
            os.makedirs(slide_block_dir)
        # load slide
        cur_slide_path = os.path.join(slide_root_dir, cur_slide)
        slide_head = openslide.OpenSlide(cur_slide_path)
        slide_w, slide_h = slide_head.dimensions
        wsi_img = slide_head.read_region(location=(0, 0), level=0, size=(slide_w, slide_h))
        np_img = np.asarray(wsi_img)[:, :, :3]
        # save block in a parallel manner
        print("....Splitting {:2d}/{:2d} {}".format(idx+1, len(slide_list), cur_slide))
        coors_list = get_splitting_coors(slide_w, slide_h, args.block_size)
        def save_block(block_info):
            x, y, w, h = block_info
            cur_block_name = cur_slide_name +"-Wstart{:05}Hstart{:05}Wlen{:05}Hlen{:05}.png".format(x, y, w, h)
            cur_block_path = os.path.join(slide_block_dir, cur_block_name)
            if not os.path.exists(cur_block_path):
                cur_block = np_img[y:y+h,x:x+w]
                io.imsave(cur_block_path, cur_block)
        Parallel(n_jobs=args.num_workers)(delayed(save_block)(block_info) for block_info in coors_list)
