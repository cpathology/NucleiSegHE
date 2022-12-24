# -*- coding: utf-8 -*-

import os, sys
import copy, argparse, pytz, shutil
from datetime import datetime

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
    
      
