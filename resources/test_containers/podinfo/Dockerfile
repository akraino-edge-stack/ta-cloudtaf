FROM alpine:3.8

ARG TOKEN=gcrf:APAeR3KQdvnxSiW2t14vxZPXP2J
ARG URL=https://artifactory-espoo1.ext.net.nokia.com/artifactory/crf-images-local/binaries/podinfo-1.4.2
RUN addgroup -S app \
    && adduser -S -g app app \
    && apk --no-cache add \
    curl openssl netcat-openbsd

WORKDIR /home/app

RUN curl -sk -u "${TOKEN}" ${URL} -o podinfo

RUN chown -R app:app ./
RUN chmod +x podinfo

USER app

CMD ["./podinfo"]
