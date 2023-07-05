# build stage
FROM paddlepaddle/paddle:2.5.0rc0-cpu as builder

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
    nltk \
    google-cloud-vision

RUN pip install --no-cache-dir slack_bolt \
    && rm -r /root/.cache/pip

COPY . ./
# Download model datas
ENV PYTHON_ENV build
RUN python3 -u app.py

COPY . ./
# production stage
FROM python:3.7-slim
# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True

COPY --from=builder /root/.cache /root/.cache
RUN ln -s /root/.cache /home/.cache
# COPY --from=builder /root/.paddleocr /root/.paddleocr
# RUN ln -s /root/.cache /home/.cache \
#     && ln -s /root/.paddleocr /home/.paddleocr

COPY --from=builder /usr/local/lib/python3.7/dist-packages /usr/local/lib/python3.7/site-packages
COPY --from=builder /usr/lib/x86_64-linux-gnu /usr/lib/x86_64-linux-gnu
COPY --from=builder /lib/x86_64-linux-gnu/libbsd.so.0 /lib/x86_64-linux-gnu/
COPY --from=builder /lib/x86_64-linux-gnu/libpcre.so.3 /lib/x86_64-linux-gnu/
COPY --from=builder /usr/bin/pdf* /usr/bin/
COPY --from=builder /usr/bin/curl /usr/bin/curl

RUN pip install --no-cache-dir gunicorn

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

ENV PORT 8080

CMD exec gunicorn --bind :$PORT --workers 2 --worker-class uvicorn.workers.UvicornWorker --threads 8 --timeout 0 app:app
