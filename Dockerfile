FROM python:3.14.3

RUN mkdir airdefense

WORKDIR /airdefense

ADD __init__.py .
ADD main.py .
ADD definitions.py .
ADD radar_mock.py .
ADD test_main.py .
ADD requirements.txt .

RUN pip install -r requirements.txt

# CMD ["ls"]
CMD ["fastapi", "dev", "main.py"]

