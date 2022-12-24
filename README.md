# NucleiSegHE
H&E ROI-Level and WSI-Level Nuclei Segmentation with HoVer-Net

* Pretrained model and demo ROIs/WSIs can be downloaded from [synapse.org](https://www.synapse.org/#!Synapse:syn50544804).

### Docker Image Preparation
* Build from Dockerfile
```
$ docker build -t nucleiseghe:chen .
```
* Or pull from Docker Hub
```
$ docker pull pingjunchen/nucleiseghe:chen
$ docker tag pingjunchen/nucleiseghe:chen nucleiseghe:chen
```

### Config Environment 
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

### ROI-Level Seg
* ROI images saved in png format
Inside the docker container under folder */App/NucleiSegHE*, run
```
$ python nuclei_seg.py
```


### WSI-Level Seg