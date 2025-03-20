FROM python:3.10

WORKDIR /api

RUN apt-get update \ 
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 poppler-utils \
    && apt-get clean


COPY ./requirements.txt /api/requirements.txt

RUN pip install --upgrade pip \
    && pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt


COPY . /api

EXPOSE 8000
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000","--reload"]