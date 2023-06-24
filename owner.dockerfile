FROM python:3

RUN mkdir -p /opt/src/owner
WORKDIR /opt/src/owner

COPY ./requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

COPY ./store/owner.py ./owner.py
COPY ./store/config.py ./config.py
COPY ./store/models.py ./models.py
COPY ./store/util.py ./util.py

ENTRYPOINT ["python", "-u", "./owner.py"]