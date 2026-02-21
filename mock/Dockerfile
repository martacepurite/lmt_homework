FROM python:3.14.3


WORKDIR /airdefense_test

COPY requirements.txt requirements.txt
COPY . .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

# EXPOSE 8000

# CMD ["python", "radar_mock.py"]
# CMD ["curl", "http://app:8000/docs/"]

