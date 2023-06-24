FROM python:3

RUN mkdir -p /opt/src/identityinit
WORKDIR /opt/src/identityinit

COPY ./requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

COPY ./identity/migrate.py ./migrate.py
COPY ./identity/config.py ./config.py
COPY ./identity/models.py ./models.py

ENTRYPOINT ["python", "-u", "./migrate.py"]