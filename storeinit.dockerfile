FROM python:3

RUN mkdir -p /opt/src/storeinit
WORKDIR /opt/src/storeinit

COPY ./requirements1.txt ./requirements.txt

RUN pip install -r ./requirements.txt

COPY ./store/migrate.py ./migrate.py
COPY ./store/config.py ./config.py
COPY ./store/models.py ./models.py

ENTRYPOINT ["python", "-u", "./migrate.py"]