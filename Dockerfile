FROM python:3.12-alpine3.17@sha256:fc34b07ec97a4f288bc17083d288374a803dd59800399c76b977016c9fe5b8f2

ENV USER=user

WORKDIR /app
COPY . /app

# Install chromium
RUN apk update && apk add --no-cache tini chromium=112.0.5615.165-r0 chromium-chromedriver=112.0.5615.165-r0

# Install python package
RUN python3 -m pip install --no-cache-dir -r requirements.txt 

# Set permission
RUN adduser -D -H -u 1000 $USER && \
    chown -R $USER:$USER /app

USER $USER

ENTRYPOINT ["tini", "--", "python", "main.py"]
