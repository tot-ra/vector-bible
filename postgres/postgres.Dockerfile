# This is installing the pgvector extension for postgres
FROM postgres:14.9

RUN apt-get update && apt-get install -y locales \
    build-essential \
    git \
    postgresql-server-dev-all \
    && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
    && locale-gen en_US.UTF-8 \
    && update-locale LANG=en_US.UTF-8 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp
RUN git clone --branch v0.7.4 https://github.com/pgvector/pgvector.git

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

WORKDIR /tmp/pgvector
RUN make
RUN make install