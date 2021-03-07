ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8

RUN apk add --no-cache python3 py3-pip

RUN pip3 install pyjwt paho-mqtt

# Copy data for add-on
COPY server.py /
RUN chmod a+x /server.py

CMD [ "/server.py", "/data/options.json" ]
