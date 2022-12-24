# -*- coding: utf-8 -*-

import os, sys
import copy, argparse, pytz
from datetime import datetime

from infer.tile import InferManager
from misc.utils import shift_contour


def set_args():
    parser = argparse.ArgumentParser(description = "Splitting WSI to blocks")
    parser.add_argument("--data_root",         type=str,       default="/Data")
    parser.add_argument("--block_dir",         type=str,       default="SlideBlocks")
    parser.add_argument("--block_seg_dir",     type=str,       default="BlockSegs")
    parser.add_argument("--slide_seg_dir",     type=str,       default="SlideSegs")    
    parser.add_argument("--gpu_ids",           type=str,       default="0,1,2,3")
    parser.add_argument("--batch_size",        type=int,       default=64)
    parser.add_argument("--num_workers",       type=int,       default=32)
    parser.add_argument("--dataset",           type=str,       default="URMC", choices=["URMC", "MDACC", "UNMC"])
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = set_args()

    # setting up infer
    os.environ['CUDA_VISIBLE_DEVICES'] = args.gpu_ids
    data_root = os.path.join(args.data_root, args.dataset)
    segcls_model_path = os.path.join(data_root, "Checkpoints", "hovernet_fast_pannuke_type_tf2pytorch.tar")
    method_args = {
        'method' : {
            'model_args' : {
                'nr_types'   : 6,
                'mode'       : "fast",
            },
            'model_path' : segcls_model_path,
        },
        'type_info_path'  : os.path.join(os.path.dirname(os.path.realpath(__file__)), "type_info.json")
    }
    infer = InferManager(**method_args)

    # set cell segmentation parameters
    run_args = {
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
    # start the slide seg/cls
    slide_block_dir = os.path.join(data_root, args.block_dir)
    block_seg_dir = os.path.join(data_root, args.seg_dir)
    slide_list = sorted([ele for ele in os.listdir(slide_block_dir) if os.path.isdir(os.path.join(slide_block_dir, ele))])
    print("{} slides ongoing SegCls....".format(len(slide_list)))
    for slide_ind, cur_slide in enumerate(slide_list):
        cur_time_str = datetime.now(pytz.timezone('America/Chicago')).strftime("%m/%d/%Y, %H:%M:%S")
        print("Start {}/{} {} @ {}".format(slide_ind+1, len(slide_list), cur_slide, cur_time_str))
        cur_slide_block_dir = os.path.join(slide_block_dir, cur_slide)
        cur_block_list = [ele for ele in os.listdir(cur_slide_block_dir) if ele.endswith(".png")]
        if len(cur_block_list) == 0:
            continue
        cur_block_seg_dir = os.path.join(block_seg_dir, cur_slide)
        run_args['input_dir'] = cur_slide_block_dir
        run_args['output_dir'] = cur_block_seg_dir
        infer.process_file_list(run_args)

        # merge block segmentations


        cur_time_str = datetime.now(pytz.timezone('America/Chicago')).strftime("%m/%d/%Y, %H:%M:%S")
        print("Finish @ {}".format(cur_time_str))
