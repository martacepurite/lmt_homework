
FROM python:3.14.3 AS base

WORKDIR /code
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

FROM base AS service_app

COPY ./app /code/

EXPOSE 8000

FROM base AS service_mock

COPY ./mock /code/