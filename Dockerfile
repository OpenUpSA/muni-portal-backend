FROM nikolaik/python-nodejs:python3.8-nodejs12

ENV POETRY_VIRTUALENVS_CREATE false
ENV PIP_NO_CACHE_DIR off
ENV PIP_DISABLE_PIP_VERSION_CHECK on
ENV PYTHONUNBUFFERED 1
ENV NODE_ENV production

RUN set -ex; \
  apt-get update; \
  # dependencies for building Python packages \
  apt-get install -y build-essential python3.7-dev; \
  # psycopg2 dependencies \
  apt-get install -y libpq-dev; \
  # git for codecov file listing \
  apt-get install -y git; \
  # cleaning up unused files \
  apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false; \
  rm -rf /var/lib/apt/lists/*

RUN pip install -U poetry

# Copy, then install requirements before copying rest for a requirements cache layer.
COPY pyproject.toml poetry.lock /tmp/
RUN set -ex; \
  cd /tmp; \
  poetry install

COPY . /app

RUN mkdir -p /var/app/ && \
  openssl ecparam -name prime256v1 -genkey -noout -out /var/app/vapid_private_key.pem && \
  openssl ec -in /var/app/vapid_private_key.pem -pubout -out /var/app/vapid_public_key.pem

ARG USER_ID=1001
ARG GROUP_ID=1001

RUN set -ex; \
  addgroup --gid $GROUP_ID --system django; \
  adduser --system --uid $USER_ID --gid $GROUP_ID django; \
  chown -R django:django /app && \
  chown -R django:django /var/app
USER django

WORKDIR /app

RUN set -ex; \
  yarn; \
  yarn build

EXPOSE 5000
CMD /app/bin/start.sh
