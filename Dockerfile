FROM python:3.6-alpine

COPY ./requirements.txt /

RUN pip install -r /requirements.txt

ENV NAME salt-truck

COPY ./ /app

WORKDIR /app

CMD ["python", "/app/app/trucksimulator.py"]
