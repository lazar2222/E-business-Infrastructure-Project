FROM python:3

RUN mkdir -p /opt/src/customer
WORKDIR /opt/src/customer

COPY ./requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

COPY ./store/customer.py ./customer.py
COPY ./store/config.py ./config.py
COPY ./store/models.py ./models.py
COPY ./store/util.py ./util.py

ENTRYPOINT ["python", "-u", "./customer.py"]