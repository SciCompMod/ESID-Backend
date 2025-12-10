FROM python:3.9

WORKDIR /worker

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 poppler-utils tesseract-ocr libtesseract-dev git \
    ninja-build libglib2.0-0 libsm6 libxrender-dev libxext6 libglx-mesa0\
    && apt-get clean
   
COPY ./requirements.txt /worker/requirements.txt

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . /worker

ENTRYPOINT celery -A app worker -Q default --loglevel=INFO --uid=nobody --gid=nogroup
