FROM python:3.11.10-slim-bullseye

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV POETRY_VERSION=2.0.1

WORKDIR /src/

RUN apt-get update && apt-get -y install libgdal-dev \
    && pip install "poetry==$POETRY_VERSION" \
    && poetry config virtualenvs.create false

COPY src/poetry.lock src/pyproject.toml ./

RUN poetry install --no-root

COPY src/ .

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.7.3/wait /wait
RUN chmod +x /wait
