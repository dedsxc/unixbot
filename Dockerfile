FROM python:3.11-alpine3.17@sha256:607af960065410fcfabfb7402ef4b7e8bf8e79691c63a99a2c14e7c07efa1774

ENV USER=user

WORKDIR /app
COPY . /app

# Install chromium
RUN apk update && apk add --no-cache chromium=112.0.5615.165-r0 chromium-chromedriver=112.0.5615.165-r0

# Install python package
RUN python3 -m pip install --no-cache-dir -r requirements.txt 

# Set permission
RUN adduser -D -H -u 1000 $USER && \
    chown -R $USER:$USER /app

USER $USER

ENTRYPOINT ["python", "main.py"]
