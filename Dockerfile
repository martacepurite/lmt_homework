
FROM python:3.14.3 AS base

WORKDIR /code
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

FROM base AS service_app

COPY ./app .

EXPOSE 8000

FROM base AS service_mock

COPY ./mock .

FROM base AS service_unit_tests

COPY ./app /code/src/app
# COPY ./mock /code/mock
COPY ./test /code/src/test
COPY ./__init__.py /code/src