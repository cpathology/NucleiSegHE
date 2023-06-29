import os
import sys
import copy
import argparse
import pytz
import shutil
import json
from datetime import datetime
import numpy as np
from skimage import io
import cv2


from misc.utils import bounding_box, random_colors

def set_args():
    parser = argparse.ArgumentParser(description = "Splitting WSI to blocks")
    parser.add_argument("--data_root",         type=str,       default="/Data")
    parser.add_argument("--dataset",           type=str,       default="LungNYU")     
    parser.add_argument("--roi_dir",           type=str,       default="RawROIs")
    parser.add_argument("--seg_dir",           type=str,       default="RawSegs")
    parser.add_argument("--overlay_dir",       type=str,       default="SegOverlays")


    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = set_args()

    # overlay cell color setting
    cell_color_dict = {0: (0, 130, 200), 1: (145, 30, 180), 2: (70, 240, 240), 3: (210, 245, 60), 
                    4: (0, 128, 128), 5: (170, 110, 40)}
    # Blue-Others / Purple-Neoplastic / Cyan-Inflammatory / Lime-Connective / Teal-Dead / Brown-Non-Neoplastic   

    # directory setting
    dataset_root_dir = os.path.join(args.data_root, "ROIs", args.dataset)
    input_roi_dir = os.path.join(dataset_root_dir, args.roi_dir)
    if not os.path.exists(input_roi_dir):
        raise ValueError(f"{input_roi_dir} directory not exist.")
    roi_lst = sorted([os.path.splitext(ele)[0] for ele in os.listdir(input_roi_dir) if ele.endswith(".png")])  
    if len(roi_lst) == 0:
        raise ValueError(f"No available png ROIs inside folder {input_roi_dir}")
    else:
        print(f"----Seg {len(roi_lst)} ROIs....")
    seg_roi_dir = os.path.join(dataset_root_dir, args.seg_dir)
    seg_lst = sorted([os.path.splitext(ele)[0] for ele in os.listdir(seg_roi_dir) if ele.endswith(".json")])
    assert len(roi_lst) == len(seg_lst), "ROI segmentation is not completed yet"
    seg_overlay_dir = os.path.join(dataset_root_dir, args.overlay_dir)
    if os.path.exists(seg_overlay_dir):
        shutil.rmtree(seg_overlay_dir)
    os.makedirs(seg_overlay_dir)

    # overlay nuclei segmentation
    for ind, cur_roi in enumerate(roi_lst):
        print(f"Overlay {ind+1}/{len(roi_lst)} ROI: {cur_roi}")
        # read image
        roi_path = os.path.join(input_roi_dir, cur_roi + ".png")
        with open(roi_path, "rb") as f:
            roi_img = io.imread(f, plugin='pil')   
        # load segmentation
        seg_path = os.path.join(seg_roi_dir, cur_roi + ".json")
        with open(seg_path, "r") as f:
            seg_dict = json.load(f)
            
        inst_dict = seg_dict["nuc"]
        for idx, [inst_id, inst_info] in enumerate(inst_dict.items()):
            inst_contour = np.expand_dims(np.array(inst_info["contour"]), axis=1)
            inst_color = cell_color_dict[inst_info["type"]]
            cv2.drawContours(roi_img, [inst_contour,], 0, inst_color, 1)
        seg_overlay_path = os.path.join(seg_overlay_dir, cur_roi + ".png") 
        with open(seg_overlay_path, "wb") as f:
            io.imsave(f, roi_img)

