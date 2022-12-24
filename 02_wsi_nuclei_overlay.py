# -*- coding: utf-8 -*-

import os, sys
import shutil, copy, glob, argparse
import pytz, pathlib, json
import openslide
from datetime import datetime
import numpy as np
from skimage import io
import cv2

import PIL
from PIL import Image
PIL.Image.MAX_IMAGE_PIXELS = 933120000
from numpy2tiff import numpy2tiff


def set_args():
    parser = argparse.ArgumentParser(description = "Overlay segmentation")
    parser.add_argument("--data_root",        type=str,       default="/Data")
    parser.add_argument("--slide_dir",        type=str,       default="RawSlides")
    parser.add_argument("--block_dir",        type=str,       default="SlideBlocks")
    parser.add_argument("--seg_dir",          type=str,       default="BlockSegs")
    parser.add_argument("--overlay_dir",      type=str,       default="OverlaySlides")

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = set_args()
    type_color_dict = {0: (0, 0, 255), 1: (255, 0, 0), 2: (0, 255, 0)}
    # Slide directory
    slide_root_dir = os.path.join(args.data_root, args.slide_dir)
    # block directory
    block_root_dir = os.path.join(args.data_root, args.block_dir)
    # seg directory
    seg_root_dir = os.path.join(args.data_root, args.seg_dir)
    # overlay directory
    overlay_root_dir = os.path.join(args.data_root, args.overlay_dir)
    if not os.path.exists(overlay_root_dir):
        os.makedirs(overlay_root_dir)

    # overlay slides one-by-one
    slide_list = sorted([ele for ele in os.listdir(slide_root_dir) if os.path.splitext(ele)[1] in [".svs", ".tiff", ".tif"]])
    for slide_idx, cur_slide in enumerate(slide_list):
        cur_time_str = datetime.now(pytz.timezone('America/Chicago')).strftime("%H:%M:%S")
        print("@ {} Start overlay {:2d}/{:2d} {}".format(cur_time_str, slide_idx+1, len(slide_list), cur_slide))
        cur_slide_name = os.path.splitext(cur_slide)[0]
        pyramid_tif_path = os.path.join(overlay_root_dir, cur_slide_name + ".tiff")
        if os.path.exists(pyramid_tif_path):
            continue
        cur_block_dir = os.path.join(block_root_dir, cur_slide_name)
        if not os.path.exists(cur_block_dir):
            continue
        cur_seg_dir = os.path.join(seg_root_dir, cur_slide_name)
        if not os.path.exists(cur_seg_dir):
            continue
        # load slide
        cur_slide_path = os.path.join(slide_root_dir, cur_slide)
        slide_head = openslide.OpenSlide(cur_slide_path)
        slide_w, slide_h = slide_head.dimensions
        slide_overlay = np.zeros((slide_h, slide_w, 3), dtype=np.uint8)
        # processing blocks one-by-one
        block_list = sorted([os.path.splitext(ele)[0] for ele in os.listdir(cur_block_dir) if ele.endswith(".png")])
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
            # read image
            cur_blcok_path = os.path.join(cur_block_dir, cur_block + ".png")
            block_overlay = io.imread(cur_blcok_path)
            # read segmentation
            cur_seg_path = os.path.join(cur_seg_dir, cur_block + ".json")
            seg_inst_dict = json.load(open(cur_seg_path, "r"))
            inst_dict = seg_inst_dict["nuc"]
            line_thickness = -1
            for idx, [inst_id, inst_info] in enumerate(inst_dict.items()):
                inst_contour = np.expand_dims(np.array(inst_info["contour"]), axis=1)
                inst_type = inst_info["type"]
                if inst_type == 3 or inst_type == 5:
                    inst_type = 0
                if inst_type == 4:
                    inst_type = 2
                inst_color = type_color_dict[inst_type]
                cv2.drawContours(block_overlay, [inst_contour,], -1, inst_color, line_thickness)
            slide_overlay[block_hstart:block_hstart+block_height,block_wstart:block_wstart+block_width] = block_overlay
        # save overlay as BigTIFF image
        big_tif_path = os.path.join(overlay_root_dir, cur_slide_name + ".tif")
        numpy2tiff(slide_overlay, big_tif_path)
        # convert the tif image to pyramid tiff
        conversion_cmd_str = " ".join(["vips", "im_vips2tiff", big_tif_path, pyramid_tif_path + ":jpeg:75,tile:256x256,pyramid"])
        os.system(conversion_cmd_str)
        os.remove(big_tif_path)
