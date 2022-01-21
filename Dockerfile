# geopandas 開発環境　channelはconda-forgeではないので、商用利用不可

FROM continuumio/miniconda3:4.10.3

RUN mkdir -p /tmp
COPY env.yml /tmp/
# RUN conda config --add channels conda-forge
# RUN conda config --remove channels defaults
RUN conda env update -f=/tmp/env.yml

RUN mkdir /code
WORKDIR /code
ADD . /code/

ENV PYTHONUNBUFFERED=0