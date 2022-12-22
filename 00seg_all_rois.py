# -*- coding: utf-8 -*-

import os, sys
import copy, argparse, pytz
from datetime import datetime

from infer.tile import InferManager


def set_args():
    parser = argparse.ArgumentParser(description = "Splitting WSI to blocks")
    parser.add_argument("--data_root",         type=str,       default="/Data")
    parser.add_argument("--block_dir",         type=str,       default="SlideBlocks")
    parser.add_argument("--seg_dir",           type=str,       default="BlockSegs")
    parser.add_argument("--gpu_ids",           type=str,       default="0,1,2,3")
    parser.add_argument("--batch_size",        type=int,       default=64)
    parser.add_argument("--num_workers",       type=int,       default=32)

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = set_args()

    slide_block_dir = os.path.join(args.data_root, args.block_dir)
    block_seg_dir = os.path.join(args.data_root, args.seg_dir)
    num_slide = len([ele for ele in os.listdir(slide_block_dir)])
    print("{} slides ongoing SegCls....".format(num_slide))
    cur_time_str = datetime.now(pytz.timezone('America/Chicago')).strftime("%m/%d/%Y, %H:%M:%S")
    print("Start @ {}".format(cur_time_str))

    # setting up infer
    os.environ['CUDA_VISIBLE_DEVICES'] = args.gpu_ids
    segcls_model_path = os.path.join(args.data_root, "Checkpoints", "hovernet_fast_pannuke_type_tf2pytorch.tar")
    method_args = {
        'method' : {
            'model_args' : {
                'nr_types'   : 6,
                'mode'       : "fast",
            },
            'model_path' : segcls_model_path,
        },
        'type_info_path'  : "./type_info.json"
    }
    infer = InferManager(**method_args)

    # run cell segmentation parameters
    run_args = {
        'input_dir': slide_block_dir,
        'output_dir': block_seg_dir,
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
    infer.process_file_list(run_args)
    cur_time_str = datetime.now(pytz.timezone('America/Chicago')).strftime("%m/%d/%Y, %H:%M:%S")
    print("Finish @ {}".format(cur_time_str))
