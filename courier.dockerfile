FROM python:3

RUN mkdir -p /opt/src/courier
WORKDIR /opt/src/courier

COPY ./requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

COPY ./store/courier.py ./courier.py
COPY ./store/config.py ./config.py
COPY ./store/models.py ./models.py
COPY ./store/util.py ./util.py

ENTRYPOINT ["python", "-u", "./courier.py"]