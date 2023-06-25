FROM python:3

RUN mkdir -p /opt/src/customer
WORKDIR /opt/src/customer

COPY ./requirements1.txt ./requirements.txt

RUN pip install -r ./requirements.txt

COPY ./store/customer.py ./customer.py
COPY ./store/config.py ./config.py
COPY ./store/models.py ./models.py
COPY ./store/util.py ./util.py
COPY ./private.key ./private.key
COPY ./public.key ./public.key
COPY ./output/Delivery.abi ./Delivery.abi
COPY ./output/Delivery.bin ./Delivery.bin

ENTRYPOINT ["python", "-u", "./customer.py"]