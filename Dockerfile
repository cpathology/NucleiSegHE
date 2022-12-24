FROM nvidia/cuda:11.3.0-base-ubuntu20.04

# Setting environment variables
ENV DEBIAN_FRONTEND noninteractive
ENV HDF5_USE_FILE_LOCKING FALSE

RUN rm /etc/apt/sources.list.d/cuda.list && \
    rm /etc/apt/sources.list.d/nvidia-ml.list && \
    apt-key del 7fa2af80 && \
    apt-get update && apt-get install -y --no-install-recommends wget && \
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-keyring_1.0-1_all.deb && \
    dpkg -i cuda-keyring_1.0-1_all.deb 

RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential libgl1-mesa-glx libglib2.0-0 libgeos-dev libvips-tools \
  curl sudo htop git wget vim ca-certificates python3-openslide \
  && rm -rf /var/lib/apt/lists/*

# Install Miniconda
WORKDIR /App
RUN chmod 777 /App
RUN curl -LO http://repo.continuum.io/miniconda/Miniconda3-py38_4.8.2-Linux-x86_64.sh \
 && bash Miniconda3-py38_4.8.2-Linux-x86_64.sh -p /App/miniconda -b \
 && rm Miniconda3-py38_4.8.2-Linux-x86_64.sh
ENV PATH=/App/miniconda/bin:$PATH
## Create a Python 3.8.3 environment
RUN /App/miniconda/bin/conda install conda-build \
 && /App/miniconda/bin/conda create -y --name py383 python=3.8.3 \
 && /App/miniconda/bin/conda clean -ya
ENV CONDA_DEFAULT_ENV=py383
ENV CONDA_PREFIX=/App/miniconda/envs/$CONDA_DEFAULT_ENV
ENV PATH=$CONDA_PREFIX/bin:$PATH

# Install python packages
RUN pip install gpustat==0.6.0 setuptools==61.2.0 pytz==2021.1 termcolor==1.1.0
RUN conda install pytorch torchvision torchaudio cudatoolkit=11.3 -c pytorch
RUN pip install openslide-python==1.1.2 tifffile==2021.10.12
RUN pip install deepdish==0.3.6 pandas==1.4.0 seaborn==0.11.2 matplotlib==3.5.0
RUN pip install scikit-learn==1.0.1 xgboost==1.5.1 statsmodels==0.13.1
RUN pip install opencv-python==4.5.4.60 scikit-image==0.18.0
RUN pip install histocartography==0.2.0
RUN pip install docopt==0.6.2 imgaug==0.4.0
RUN pip install lxml==4.6.3 shapely==1.8.0

# Set environment variables
WORKDIR /.dgl
RUN chmod 777 /.dgl
WORKDIR /.local
RUN chmod 777 /.local
WORKDIR /Data
RUN chmod 777 /Data
WORKDIR /App/NucleiSegHE

CMD ["/bin/bash"]