# -*- coding: utf-8 -*-

import os
import argparse
import pytz
from datetime import datetime

from infer.tile import InferManager


def set_args():
    parser = argparse.ArgumentParser(description = "Splitting WSI to blocks")
    parser.add_argument("--data_root",         type=str,       default="/Data")
    parser.add_argument("--checkpoint_dir",    type=str,       default="Checkpoints")
    parser.add_argument("--dataset",           type=str,       default="LungNYU")      
    parser.add_argument("--roi_dir",           type=str,       default="RawROIs")
    parser.add_argument("--seg_dir",           type=str,       default="RawSegs")
    parser.add_argument("--gpu_ids",           type=str,       default="0")
    parser.add_argument("--batch_size",        type=int,       default=16)
    parser.add_argument("--num_workers",       type=int,       default=4)

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = set_args()
    os.environ['CUDA_VISIBLE_DEVICES'] = args.gpu_ids

    # directory setting
    dataset_root_dir = os.path.join(args.data_root, args.dataset)
    input_roi_dir = os.path.join(dataset_root_dir, args.roi_dir)
    if not os.path.exists(input_roi_dir):
        sys.exit("{} directory not exist.".format(input_roi_dir))
    roi_lst = sorted([ele for ele in os.listdir(input_roi_dir) if ele.endswith(".png")])  
    if len(roi_lst) == 0:
        sys.exit("No available png ROIs inside folder {}".format(input_roi_dir))
    else:
        print("----Seg {} ROIs....".format(len(roi_lst)))
    seg_roi_dir = os.path.join(dataset_root_dir, args.seg_dir)
    if os.path.exists(seg_roi_dir):
        shutil.rmtree(seg_roi_dir)
    os.makedirs(seg_roi_dir)

    # model setting
    checkpoint_dir = os.path.join(args.data_root, args.checkpoint_dir)
    seg_model_path = os.path.join(checkpoint_dir, "hovernet_fast_pannuke_type_tf2pytorch.tar")
    seg_type_info_path = os.path.join(checkpoint_dir, "type_info.json")
    if not os.path.exists(seg_model_path) or not os.path.exists(seg_type_info_path):
        sys.exit("segemtnation model doesnot exist.")
    model_args = {
        "method" : {
            "model_args" : {
                "nr_types"   : 6,
                "mode"       : "fast",
            },
            "model_path"     : seg_model_path,
        },
        "type_info_path"     : seg_type_info_path
    }
    infer_model = InferManager(**model_args)
    # run cell segmentation parameters
    run_args = {
        'input_dir': input_roi_dir,
        'output_dir': seg_roi_dir,
        'batch_size' : args.batch_size,
        'nr_inference_workers' : args.num_workers,
        'nr_post_proc_workers' : args.num_workers,
        'patch_input_shape' : 256,
        'patch_output_shape': 164,
        'mem_usage': 0.8,
        'draw_dot': False,
        'save_qupath': False,
        'save_raw_map': False,
    }

    cur_time_str = datetime.now(pytz.timezone('America/Chicago')).strftime("%m/%d/%Y, %H:%M:%S")
    print("Start @ {}".format(cur_time_str))
    infer_model.process_file_list(run_args)
    cur_time_str = datetime.now(pytz.timezone('America/Chicago')).strftime("%m/%d/%Y, %H:%M:%S")
    print("Finish @ {}".format(cur_time_str))
