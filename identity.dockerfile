FROM python:3

RUN mkdir -p /opt/src/identity
WORKDIR /opt/src/identity

COPY ./requirements1.txt ./requirements.txt

RUN pip install -r ./requirements.txt

COPY ./identity/app.py ./app.py
COPY ./identity/config.py ./config.py
COPY ./identity/models.py ./models.py

ENTRYPOINT ["python", "-u", "./app.py"]