FROM paddlepaddle/paddle:2.4.1-gpu-cuda11.2-cudnn8.2-trt8.0

ENV DEBIAN_FRONTEND=noninteractive
ENV DEBCONF_NOWARNINGS=yes
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get install -y \
        poppler-utils \
        libpoppler-dev \
        wget git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* /var/tmp/* \
    && mkdir -p /home/paper-summarizer

WORKDIR /home/paper-summarizer

RUN pip install --no-cache-dir opencv-python-headless \
    arxiv \
    paddleocr \
    pdf2image \
    uvicorn \
    fastapi[uvicorn] \
    apscheduler \
    PyPDF2 \
    openai \
    python-dotenv \
    transformers \
    nltk
