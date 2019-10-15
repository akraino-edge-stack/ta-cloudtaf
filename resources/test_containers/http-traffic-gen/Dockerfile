FROM alpine:3.7
MAINTAINER Tamas Kopcso <tamas.kopcso@nokia.com>

RUN apk update
RUN apk add python
RUN apk add py-pip
RUN pip install requests
RUN mkdir /etc/http_traffic_gen
COPY http_traffic_gen.py /etc/http_traffic_gen/http_traffic_gen.py 
CMD ["python", "/etc/http_traffic_gen/http_traffic_gen.py"]
