FROM python:3.6-alpine

#WORKDIR /app

#ENV BUILD_LIST git

#RUN apk add --update $BUILD_LIST \
#    && pip install pipenv \
#    && pipenv --python=python3.6 \
#    && pipenv install \
#    && apk del $BUILD_LIST \
#    && rm -rf /var/cache/apk/*
RUN pip install flask requests
COPY blockchain.py /blockchain.py
COPY templates /templates
EXPOSE 5000

ENTRYPOINT [ "python", "/blockchain.py", "--port", "5000"  ]
