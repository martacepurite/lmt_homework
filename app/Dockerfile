FROM python:3.14.3


WORKDIR /airdefense

COPY requirements.txt requirements.txt
COPY . .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 8000

# CMD ["fastapi", "run", "main.py", "--port", "8000"]
# CMD ["pytest"]

