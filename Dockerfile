FROM alpine

WORKDIR /app

COPY . .

RUN apk -U add python3 py3-pip \
 && pip3 install -r requirements.txt

CMD python3 -u main.py

EXPOSE 9000
