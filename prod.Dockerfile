FROM python:3.7-alpine as base

FROM base as builder 
RUN mkdir /install
RUN apk update && apk add postgresql-dev gcc musl-dev
WORKDIR /install
COPY requirements.txt /requirements.txt
RUN pip install --target="--prefix=/install" -r /requirements.txt  

FROM base
COPY --from=builder /install /usr/local
RUN pip install alembic python-dateutil
RUN apk update && apk add libpq
ADD . /app
WORKDIR /app
EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
