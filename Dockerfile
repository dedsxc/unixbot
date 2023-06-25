FROM python:3.11-alpine3.17


ARG UID="1000"
ARG USER="user"

WORKDIR /app

COPY . /app

RUN python3 -m pip install --no-cache-dir -r requirements.txt && \
    adduser -D -H -u $UID $USER && \
    chown -R $USER:$USER /app

USER $USER

ENTRYPOINT ["python", "main.py"]
