# -*- coding: utf-8 -*-

import os, sys
import copy, argparse, pytz, shutil, json
from datetime import datetime
import numpy as np
from skimage import io
import cv2

from misc.utils import bounding_box, random_colors

def set_args():
    parser = argparse.ArgumentParser(description = "Splitting WSI to blocks")
    parser.add_argument("--data_root",         type=str,       default="/Data")
    parser.add_argument("--dataset",           type=str,       default="DatasetA", choices=["DatasetA", "DatasetB"])     
    parser.add_argument("--roi_dir",           type=str,       default="RawROIs")
    parser.add_argument("--seg_dir",           type=str,       default="RawSegs")


    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = set_args()

    # overlay cell color setting
    cell_color_dict = {0: (0, 130, 200), 1: (145, 30, 180), 2: (70, 240, 240), 3: (210, 245, 60), 
                    4: (0, 128, 128), 5: (170, 110, 40)}
    # Blue-Others / Purple-Neoplastic / Cyan-Inflammatory / Lime-Connective / Teal-Dead / Brown-Non-Neoplastic   

    # directory setting
    dataset_root_dir = os.path.join(args.data_root, "DemoROIs", args.dataset)
    input_roi_dir = os.path.join(dataset_root_dir, args.roi_dir)
    if not os.path.exists(input_roi_dir):
        sys.exit("{} directory not exist.".format(input_roi_dir))
    roi_lst = sorted([os.path.splitext(ele)[0] for ele in os.listdir(input_roi_dir) if ele.endswith(".png")])  
    if len(roi_lst) == 0:
        sys.exit("No available png ROIs inside folder {}".format(input_roi_dir))
    else:
        print("----Seg {} ROIs....".format(len(roi_lst)))
    seg_roi_dir = os.path.join(dataset_root_dir, args.seg_dir)
    seg_lst = sorted([os.path.splitext(ele)[0] for ele in os.listdir(input_roi_dir) if ele.endswith(".json")])
    assert len(roi_lst) == len(seg_lst), "ROI segmentation is not completed yet"

    for ind, cur_roi in enumerate(roi_lst):
        print("Overlay {}/{} ROI: {}".format(ind+1, len(roi_lst), cur_roi))
        # read image
        roi_path = os.path.join(input_roi_dir, cur_roi + ".png")
        roi_img = io.imread(roi_path)   
        # load segmentation
        seg_path = os.path.join(seg_roi_dir, cur_roi + ".json")
        seg_dict = json.load(open(seg_path, "r"))
        inst_dict = seg_dict["nuc"]
        for idx, [inst_id, inst_info] in enumerate(inst_dict.items()):
            inst_contour = np.expand_dims(np.array(inst_info["contour"]), axis=1)
            if len(inst_contour) != 1:
                print("{} contours.".format(len(inst_contour)))
            inst_color = cell_color_dict[inst_info["type"]]
            cv2.drawContours(roi_img, [inst_contour,], 0, inst_color, 1)             