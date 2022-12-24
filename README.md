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
  --name nucleiseghe:chen nucleiseghe:chen
```


### ROI-Level Seg


### WSI-Level Seg