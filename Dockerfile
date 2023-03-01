FROM python:3.10

ARG UID=1000
ARG GID=1000

# RUN apt update
# RUN apt upgrade -y
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
WORKDIR /app
RUN groupadd -g "${GID}" -r pcr-qr-healthcheck \
    && useradd -d '/app' -g pcr-qr-healthcheck -l -r -u "${UID}" pcr-qr-healthcheck \
    && chown pcr-qr-healthcheck:pcr-qr-healthcheck -R '/app'
USER pcr-qr-healthcheck
# COPY ./app /app
# COPY ./config /config
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# CMD ["ls"]