# -*- coding: utf-8 -*-

import os, sys
import glob, inspect, logging, shutil, struct
import itertools, colorsys, random
import numpy as np
from scipy import ndimage
import cv2



####
def bounding_box(img):
    rows = np.any(img, axis=1)
    cols = np.any(img, axis=0)
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    # due to python indexing, need to add 1 to max
    # else accessing will be 1px in the box, not out
    rmax += 1
    cmax += 1
    return [rmin, rmax, cmin, cmax]


####
def random_colors(N, bright=True):
    """
    Generate random colors.
    To get visually distinct colors, generate them in HSV space then
    convert to RGB.
    """
    random.seed(1234)
    brightness = 1.0 if bright else 0.7
    hsv = [(i / N, 1, brightness) for i in range(N)]
    colors = list(map(lambda c: colorsys.hsv_to_rgb(*c), hsv))
    random.shuffle(colors)
    return colors


####
def get_splitting_coors(wsi_w, wsi_h, block_size):
    def split_coor(ttl_len, sub_len):
        split_num = int(np.floor((ttl_len + sub_len / 2) / sub_len))
        split_pair = [(num * sub_len, sub_len) for num in range(split_num-1)]
        split_pair.append(((split_num-1) * sub_len, ttl_len - (split_num-1) * sub_len))
        return split_pair

    w_pairs = split_coor(wsi_w, block_size)
    h_pairs = split_coor(wsi_h, block_size)
    coors_list = [(ele[0][0], ele[1][0], ele[0][1], ele[1][1]) for ele in list(itertools.product(w_pairs, h_pairs))]

    return coors_list


####    
def shift_contour(cnt_dict, wstart, hstart):
    ## centroid
    cnt_dict["centroid"][0] += wstart
    cnt_dict["centroid"][1] += hstart
    ## bbox
    box_len = len(cnt_dict["bbox"])
    for ind in range(box_len):
        cnt_dict["bbox"][ind][0] += wstart
        cnt_dict["bbox"][ind][1] += hstart
    ## contour
    cnt_len = len(cnt_dict["contour"])
    for ind in range(cnt_len):
        cnt_dict["contour"][ind][0] += wstart
        cnt_dict["contour"][ind][1] += hstart

    return cnt_dict


####
def normalize(mask, dtype=np.uint8):
    return (255 * mask / np.amax(mask)).astype(dtype)


####
def get_bounding_box(img):
    """Get bounding box coordinate information."""
    rows = np.any(img, axis=1)
    cols = np.any(img, axis=0)
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    # due to python indexing, need to add 1 to max
    # else accessing will be 1px in the box, not out
    rmax += 1
    cmax += 1
    return [rmin, rmax, cmin, cmax]


####
def cropping_center(x, crop_shape, batch=False):
    """Crop an input image at the centre.

    Args:
        x: input array
        crop_shape: dimensions of cropped array
    
    Returns:
        x: cropped array
    
    """
    orig_shape = x.shape
    if not batch:
        h0 = int((orig_shape[0] - crop_shape[0]) * 0.5)
        w0 = int((orig_shape[1] - crop_shape[1]) * 0.5)
        x = x[h0 : h0 + crop_shape[0], w0 : w0 + crop_shape[1]]
    else:
        h0 = int((orig_shape[1] - crop_shape[0]) * 0.5)
        w0 = int((orig_shape[2] - crop_shape[1]) * 0.5)
        x = x[:, h0 : h0 + crop_shape[0], w0 : w0 + crop_shape[1]]
    return x


####
def rm_n_mkdir(dir_path):
    """Remove and make directory."""
    if os.path.isdir(dir_path):
        shutil.rmtree(dir_path)
    os.makedirs(dir_path)


####
def mkdir(dir_path):
    """Make directory."""
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)


####
def get_inst_centroid(inst_map):
    """Get instance centroids given an input instance map.

    Args:
        inst_map: input instance map
    
    Returns:
        array of centroids
    
    """
    inst_centroid_list = []
    inst_id_list = list(np.unique(inst_map))
    for inst_id in inst_id_list[1:]:  # avoid 0 i.e background
        mask = np.array(inst_map == inst_id, np.uint8)
        inst_moment = cv2.moments(mask)
        inst_centroid = [
            (inst_moment["m10"] / inst_moment["m00"]),
            (inst_moment["m01"] / inst_moment["m00"]),
        ]
        inst_centroid_list.append(inst_centroid)
    return np.array(inst_centroid_list)


####
def center_pad_to_shape(img, size, cval=255):
    """Pad input image."""
    # rounding down, add 1
    pad_h = size[0] - img.shape[0]
    pad_w = size[1] - img.shape[1]
    pad_h = (pad_h // 2, pad_h - pad_h // 2)
    pad_w = (pad_w // 2, pad_w - pad_w // 2)
    if len(img.shape) == 2:
        pad_shape = (pad_h, pad_w)
    else:
        pad_shape = (pad_h, pad_w, (0, 0))
    img = np.pad(img, pad_shape, "constant", constant_values=cval)
    return img


####
def color_deconvolution(rgb, stain_mat):
    """Apply colour deconvolution."""
    log255 = np.log(255)  # to base 10, not base e
    rgb_float = rgb.astype(np.float64)
    log_rgb = -((255.0 * np.log((rgb_float + 1) / 255.0)) / log255)
    output = np.exp(-(log_rgb @ stain_mat - 255.0) * log255 / 255.0)
    output[output > 255] = 255
    output = np.floor(output + 0.5).astype("uint8")
    return output


####
def log_debug(msg):
    frame, filename, line_number, function_name, lines, index = inspect.getouterframes(
        inspect.currentframe()
    )[1]
    line = lines[0]
    indentation_level = line.find(line.lstrip())
    logging.debug("{i} {m}".format(i="." * indentation_level, m=msg))


####
def log_info(msg):
    frame, filename, line_number, function_name, lines, index = inspect.getouterframes(
        inspect.currentframe()
    )[1]
    line = lines[0]
    indentation_level = line.find(line.lstrip())
    logging.info("{i} {m}".format(i="." * indentation_level, m=msg))


def remove_small_objects(pred, min_size=64, connectivity=1):
    """Remove connected components smaller than the specified size.

    This function is taken from skimage.morphology.remove_small_objects, but the warning
    is removed when a single label is provided. 

    Args:
        pred: input labelled array
        min_size: minimum size of instance in output array
        connectivity: The connectivity defining the neighborhood of a pixel. 
    
    Returns:
        out: output array with instances removed under min_size

    """
    out = pred

    if min_size == 0:  # shortcut for efficiency
        return out

    if out.dtype == bool:
        selem = ndimage.generate_binary_structure(pred.ndim, connectivity)
        ccs = np.zeros_like(pred, dtype=np.int32)
        ndimage.label(pred, selem, output=ccs)
    else:
        ccs = out

    try:
        component_sizes = np.bincount(ccs.ravel())
    except ValueError:
        raise ValueError(
            "Negative value labels are not supported. Try "
            "relabeling the input with `scipy.ndimage.label` or "
            "`skimage.morphology.label`."
        )

    too_small = component_sizes < min_size
    too_small_mask = too_small[ccs]
    out[too_small_mask] = 0

    return out


def numpy2tiff(image, path):
    def tiff_tag(tag_code, datatype, values):
        types = {'<H': 3, '<L': 4, '<Q': 16}
        datatype_code = types[datatype]
        number = 1 if isinstance(values, int) else len(values)
        if number == 1:
            values_bytes = struct.pack(datatype, values)
        else:
            values_bytes = struct.pack('<' + (datatype[-1:] * number), *values)
        tag_bytes = struct.pack('<HHQ', tag_code, datatype_code, number) + values_bytes
        tag_bytes += b'\x00' * (20 - len(tag_bytes))
        return tag_bytes

    image_bytes = image.shape[0] * image.shape[1] * image.shape[2]
    with open(path, 'wb+') as f:
        image.reshape((image_bytes,))
        f.write(b'II')
        f.write(struct.pack('<H', 43))  # Version number
        f.write(struct.pack('<H', 8))  # Bytesize of offsets
        f.write(struct.pack('<H', 0))  # always zero
        f.write(struct.pack('<Q', 16 + image_bytes))  # Offset to IFD
        for offset in range(0, image_bytes, 2 ** 20):
            f.write(image[offset:offset + 2 ** 20].tobytes())
        f.write(struct.pack('<Q', 8))  # Number of tags in IFD
        f.write(tiff_tag(256, '<L', image.shape[1]))  # ImageWidth tag
        f.write(tiff_tag(257, '<L', image.shape[0]))  # ImageLength tag
        f.write(tiff_tag(258, '<H', (8, 8, 8)))  # BitsPerSample tag
        f.write(tiff_tag(262, '<H', 2))  # PhotometricInterpretation tag
        f.write(tiff_tag(273, '<H', 16))  # StripOffsets tag
        f.write(tiff_tag(277, '<H', 3))  # SamplesPerPixel
        f.write(tiff_tag(278, '<Q', image_bytes // 8192))  # RowsPerStrip
        f.write(tiff_tag(279, '<Q', image_bytes))  # StripByteCounts
        f.write(struct.pack('<Q', 0))  # Offset to next IFD