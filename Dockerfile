FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH "${PYTHONPATH}:/code"

WORKDIR /code

COPY requirements.txt requirements.txt
RUN \
    pip install --no-cache-dir --upgrade pip flake8 black && \
    pip install -r /code/requirements.txt
