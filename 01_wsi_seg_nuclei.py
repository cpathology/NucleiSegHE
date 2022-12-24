# -*- coding: utf-8 -*-

import os, sys
import copy, argparse, pytz, shutil, json
from datetime import datetime

from infer.tile import InferManager
from misc.utils import shift_contour


def set_args():
    parser = argparse.ArgumentParser(description = "Splitting WSI to blocks")
    parser.add_argument("--data_root",         type=str,       default="/Data")
    parser.add_argument("--checkpoint_dir",    type=str,       default="Checkpoints")
    parser.add_argument("--dataset",           type=str,       default="CLL", choices=["CLL", "NLPHL", "Lung"])    
    parser.add_argument("--block_dir",         type=str,       default="SlideBlocks")
    parser.add_argument("--block_seg_dir",     type=str,       default="BlockSegs")
    parser.add_argument("--slide_seg_dir",     type=str,       default="SlideSegs")    
    parser.add_argument("--gpu_ids",           type=str,       default="0,1,2,3")
    parser.add_argument("--batch_size",        type=int,       default=64)
    parser.add_argument("--num_workers",       type=int,       default=32)

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = set_args()
    os.environ['CUDA_VISIBLE_DEVICES'] = args.gpu_ids

    # directory setting
    dataset_root_dir = os.path.join(args.data_root, "WSIs", args.dataset)
    slide_block_dir = os.path.join(dataset_root_dir, args.block_dir)
    if not os.path.exists(slide_block_dir):
        sys.exit("{} directory not exist.".format(slide_block_dir))
    slide_list = sorted([ele for ele in os.listdir(slide_block_dir) if os.path.isdir(os.path.join(slide_block_dir, ele))])    
    if len(slide_list) == 0:
        sys.exit("No available SlideBlocks inside folder {}".format(slide_block_dir))
    else:
        print("----Seg {} WSIs....".format(len(slide_list)))
    block_seg_dir = os.path.join(dataset_root_dir, args.block_seg_dir)
    if os.path.exists(block_seg_dir):
        shutil.rmtree(block_seg_dir)
    os.makedirs(block_seg_dir)    
    slide_seg_dir = os.path.join(dataset_root_dir, args.slide_seg_dir)
    if os.path.exists(slide_seg_dir):
        shutil.rmtree(slide_seg_dir)
    os.makedirs(slide_seg_dir)      


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
        infer_model.process_file_list(run_args)

        # merge block segmentations
        print("Merge block segmentations...")
        slide_nuc_dict = {}
        slide_nuc_id = 1
        block_list = sorted([os.path.splitext(ele)[0] for ele in os.listdir(cur_block_seg_dir) if ele.endswith(".json")])
        for block_idx, cur_block in enumerate(block_list):
            wstart_pos = cur_block.index("Wstart")
            hstart_pos = cur_block.index("Hstart")
            wlen_pos = cur_block.index("Wlen")
            hlen_pos = cur_block.index("Hlen")
            block_wstart = int(cur_block[wstart_pos+len("Wstart"):hstart_pos])
            block_hstart = int(cur_block[hstart_pos+len("Hstart"):wlen_pos])
            block_width = int(cur_block[wlen_pos+len("Wlen"):hlen_pos])
            block_height = int(cur_block[hlen_pos+len("Hlen"):len(cur_block)])
            # read segmentation
            cur_seg_path = os.path.join(cur_block_seg_dir, cur_block + ".json")
            seg_inst_dict = json.load(open(cur_seg_path, "r"))
            nuc_dict = seg_inst_dict["nuc"]
            # traverse nucleus one-by-one
            for ind, cur_inst in enumerate(nuc_dict.keys()):
                slide_nuc_dict[str(slide_nuc_id)] = shift_contour(nuc_dict[cur_inst], block_wstart, block_hstart)
                slide_nuc_id += 1
        # save json file
        slide_json_path = os.path.join(slide_seg_dir, cur_slide + ".json")
        with open(slide_json_path, 'w') as fp:
            json.dump(slide_nuc_dict, fp)        
        cur_time_str = datetime.now(pytz.timezone('America/Chicago')).strftime("%m/%d/%Y, %H:%M:%S")
        print("Finish @ {}".format(cur_time_str))
