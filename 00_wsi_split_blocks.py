import os
import shutil
import argparse
import pytz
import openslide
import numpy as np
from skimage import io
from datetime import datetime
from concurrent import futures

from misc.utils import get_splitting_coors


def set_args():
    parser = argparse.ArgumentParser(description = "Splitting WSI to blocks")
    parser.add_argument("--data_root",         type=str,       default="/Data")
    parser.add_argument("--slide_dir",         type=str,       default="RawSlides")
    parser.add_argument("--block_dir",         type=str,       default="SlideBlocks")
    parser.add_argument("--block_size",        type=int,       default=5000)
    parser.add_argument("--num_workers",       type=int,       default=64)
    parser.add_argument("--dataset",           type=str,       default="CLL")    
    args = parser.parse_args()
    return args


def save_block(block_info, cur_slide_name, slide_block_dir, np_img):
    x, y, w, h = block_info
    cur_block_name = f"{cur_slide_name}-Wstart{x:05d}Hstart{y:05d}Wlen{w:05d}Hlen{h:05d}.png"
    cur_block_path = os.path.join(slide_block_dir, cur_block_name)
    if not os.path.exists(cur_block_path):
        cur_block = np_img[y : y + h, x : x + w]
        io.imsave(cur_block_path, cur_block)


if __name__ == "__main__":
    args = set_args()
    # Slide directory
    dataset_root_dir = os.path.join(args.data_root, "WSIs", args.dataset)
    slide_root_dir = os.path.join(dataset_root_dir, args.slide_dir)
    slide_list = sorted([ele for ele in os.listdir(slide_root_dir) if os.path.splitext(ele)[1] in [".svs", ".tiff"]])
    # Block directory
    block_root_dir = os.path.join(dataset_root_dir, args.block_dir)
    os.makedirs(block_root_dir, exist_ok=True)

    # split slides one-by-one
    with futures.ThreadPoolExecutor(max_workers=args.num_workers) as executor:
        for idx, cur_slide in enumerate(slide_list):
            cur_time_str = datetime.now(pytz.timezone("America/Chicago")).strftime("%m/%d/%Y, %H:%M:%S")
            print("Start @ {}".format(cur_time_str))
            cur_slide_name = os.path.splitext(cur_slide)[0]
            # prepare block directory
            slide_block_dir = os.path.join(block_root_dir, cur_slide_name)
            os.makedirs(slide_block_dir, exist_ok=True)
            # load slide
            cur_slide_path = os.path.join(slide_root_dir, cur_slide)
            slide_head = openslide.OpenSlide(cur_slide_path)
            slide_w, slide_h = slide_head.dimensions
            wsi_img = slide_head.read_region(location=(0, 0), level=0, size=(slide_w, slide_h))
            np_img = np.asarray(wsi_img)[:, :, :3]
            # save block in a parallel manner
            print("....Splitting {:2d}/{:2d} {}".format(idx + 1, len(slide_list), cur_slide))
            coors_list = get_splitting_coors(slide_w, slide_h, args.block_size)
            block_info_list = [(block_info, cur_slide_name, slide_block_dir, np_img) for block_info in coors_list]
            # submit block saving tasks to the executor
            futures_list = [executor.submit(save_block, *block_info) for block_info in block_info_list]
            # wait for all tasks to complete
            for future in futures.as_completed(futures_list):
                future.result()
