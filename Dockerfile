FROM nvidia/cuda:12.1.0-devel-ubuntu22.04

# Setting environment variables
ENV DEBIAN_FRONTEND noninteractive
ENV HDF5_USE_FILE_LOCKING FALSE
ENV NUMBA_CACHE_DIR /tmp

# set web proxy
ENV http_proxy http://1mcwebproxy01.mdanderson.edu:3128
ENV https_proxy http://1mcwebproxy01.mdanderson.edu:3128
ENV HTTP_PROXY http://1mcwebproxy01.mdanderson.edu:3128
ENV HTTPS_PROXY http://1mcwebproxy01.mdanderson.edu:3128

# install libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential libgl1-mesa-glx libglib2.0-0 libgeos-dev libvips-tools \
  sudo curl wget htop git vim ca-certificates python3-openslide python3-pip python3-dev \
  && rm -rf /var/lib/apt/lists/*

# Install python packages
RUN pip install gpustat==0.6.0 setuptools==61.2.0 pytz==2021.1 termcolor==1.1.0
RUN pip install openslide-python==1.2.0 tifffile==2021.10.12
RUN pip install opencv-python==4.5.4.60 scikit-image==0.18.0
RUN pip install joblib==1.2.0 tqdm==4.64.0 docopt==0.6.2 imgaug==0.4.0
RUN pip install torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1 torchinfo==1.8.0 torchmetrics==1.4.0 

# Set environment variables
WORKDIR /.dgl
RUN chmod 777 /.dgl
WORKDIR /.local
RUN chmod 777 /.local
WORKDIR /Data
RUN chmod 777 /Data
WORKDIR /App/

CMD ["/bin/bash"]
# CMD["/usr/bin/python3", "python_script.py"]