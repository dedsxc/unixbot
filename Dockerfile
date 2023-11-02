FROM python:3.11-alpine3.17


ARG UID="1000"
ARG USER="user"

WORKDIR /app
COPY . /app

# Install chromium
RUN apk update && apk add --no-cache chromium=112.0.5615.165-r0 chromium-chromedriver=112.0.5615.165-r0
RUN python3 -m pip install --no-cache-dir -r requirements.txt && \
    adduser -D -H -u $UID $USER && \
    chown -R $USER:$USER /app

USER $USER

ENTRYPOINT ["python", "main.py"]
