FROM paddlepaddle/paddle:2.5.0rc0-cpu

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
    gunicorn \
    slack_bolt

# WORKDIR /app
# COPY . ./
# # Download model datas
# RUN python3 -u app.py

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Download model datas
ENV PYTHON_ENV build
RUN python3 -u app.py

ENV PORT 8080

CMD exec gunicorn --bind :$PORT --workers 4 --worker-class uvicorn.workers.UvicornWorker --threads 2 --timeout 0 app:app
