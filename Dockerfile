################################################################################
# BASE IMAGE WITH SOURCES AND DEPENDENCIES
################################################################################

FROM python:3.8-slim as base

LABEL maintainer="Quantumsoft LLC"

ENV APP_HOME=/app \
    PYTHONPATH=${APP_HOME}

RUN mkdir -p ${APP_HOME}
WORKDIR ${APP_HOME}

COPY ./requirements.txt ${APP_HOME}/requirements.txt

RUN set -xe \
    && pip install --upgrade pip setuptools \
    && pip install --no-cache-dir -r requirements.txt \
    && python -m spacy download en_core_web_sm \
    && python -m nltk.downloader all


COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]

################################################################################
# IMAGE WITH SERVICE SOURCES
################################################################################

FROM base as sources

COPY . ${APP_HOME}

################################################################################
# RELEASE IMAGE
################################################################################

FROM sources as release

# ------------------------------------------------------------------------------
# Set environment
# ------------------------------------------------------------------------------

ARG ENVIRONEMENT=${ENVIRONEMENT}
ARG PORT=${PORT}
ARG SERVICE_NAME=${SERVICE_NAME}
ARG FLASK_RUN_HOST=0.0.0.0

ENV ENVIRONMENT=${ENVIRONEMENT} \
    PORT=${PORT} \
    FLASK_APP=${SERVICE_NAME} \
    FLASK_ENV=${ENVIRONEMENT} \
    FLASK_RUN_HOST=${FLASK_RUN_HOST}

# ------------------------------------------------------------------------------
# Expose HTTP port
# ------------------------------------------------------------------------------

EXPOSE ${PORT}
