FROM python:3.12.0a7-alpine3.17

LABEL maintainer="Maryam Kermanshahani  <maryam.kermanshahani6079@gmail.com>"

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY .. .

CMD ["python", "/app/main.py"]