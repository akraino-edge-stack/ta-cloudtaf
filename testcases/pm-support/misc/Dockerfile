FROM alpine:latest

ADD custom_metrics_test.py /

RUN apk add --no-cache py-pip \
&& pip install --upgrade pip \
&& pip install prometheus_client

CMD ["python", "./custom_metrics_test.py"]
