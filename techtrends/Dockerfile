# I used the Python base image 3.8  according to the project instructions
FROM python:3.8
LABEL maintainer = "Sepid"

COPY . /app
WORKDIR /app

ADD . .

RUN pip install -r requirements.txt

CMD python init_db.py ; python -u app.py

EXPOSE 3111