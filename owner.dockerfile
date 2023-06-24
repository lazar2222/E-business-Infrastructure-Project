FROM bde2020/spark-python-template:3.3.0-hadoop3.3

RUN apk add build-base
RUN apk add python3-dev
RUN apk add libffi-dev
RUN apk add py-cryptography

COPY ./requirements2.txt /app/requirements.txt

RUN cd /app && pip3 install -r ./requirements.txt

COPY ./store/owner.py /app/owner.py
COPY ./store/config.py /app/config.py
COPY ./store/models.py /app/models.py
COPY ./store/util.py /app/util.py

ENTRYPOINT ["python3", "-u", "/app/owner.py"]