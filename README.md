# NucleiSegHE
H&E ROI-Level and WSI-Level Nuclei Segmentation with HoVer-Net
* Pretrained model and demo ROIs/WSIs can be downloaded from [synapse.org](https://www.synapse.org/#!Synapse:syn50545401/files).
![Demo segmented nuclei overlaying ROI](zoo/Demo_ROI_Seg_Overlay.PNG)

## Environment Configuration

### Prepare docker image
* Build from Dockerfile
```
$ docker build -t nucleiseghe:chen .
```
* Or pull from Docker Hub
```
$ docker pull pingjunchen/nucleiseghe:chen
$ docker tag pingjunchen/nucleiseghe:chen nucleiseghe:chen
```

### Setup docker container
* Start docker container (Specify CODE_ROOT & DATA_ROOT)
```
$ docker run -it --rm --user $(id -u):$(id -g) \
  -v ${CODE_ROOT}:/App/NucleiSegHE \
  -v ${DATA_ROOT}:/Data \
  --shm-size=224G --gpus '"device=0,1"' --cpuset-cpus=0-15 \
  --name nucleiseghe_chen nucleiseghe:chen
```
For example:
```
$ docker run -it --rm  --user $(id -u):$(id -g) \
  -v /rsrch1/ip/pchen6/Codes/CHEN/NucleiSegHE:/App/NucleiSegHE \
  -v /rsrch1/ip/pchen6/NucleiSegData:/Data \
  --shm-size=224G --gpus '"device=0,1"' --cpuset-cpus=0-15 \
  --name nucleiseghe_chen nucleiseghe:chen
```

## ROI-Level Seg (png format supported)
Inside the docker container, enter */App/NucleiSegHE*
```
# Nuclei Segmentation
$ python 01_roi_seg.py --dataset LungNYU
# Nuclei Overlay
$ python 02_roi_seg_overlay.py --dataset LungNYU
```

## WSI-Level Seg (svs/tiff format supported)
Inside the docker container, enter */App/NucleiSegHE*
```
# Split WSI into smaller blocks (5000 x 5000)
$ python 00_wsi_split.py --dataset CLL
# Block-wise WSI nuclei segmentation and merging
$ python 01_wsi_seg.py --dataset CLL
# Nuclei overlay to the entire WSI
$ python 01_wsi_seg.py --dataset CLL
```