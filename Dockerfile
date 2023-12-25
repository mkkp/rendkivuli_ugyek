# syntax=docker/dockerfile:1
FROM python:3.10-slim@sha256:2bac43769ace90ebd3ad83e5392295e25dfc58e58543d3ab326c3330b505283d

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app
COPY . .

# install app dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*    

RUN python3 -m pip install --upgrade pip
RUN pip install -r requirements.txt

# Clone from GIT
RUN git clone https://github.com/mkkp/rendkivuli_ugyek.git .

VOLUME /usr/src/app/db/app.db
VOLUME /usr/src/app/static/upload

EXPOSE 5000

ENTRYPOINT ["gunicorn"]

CMD ["-w=4", "-b", "0.0.0.0:5000", "app:app"]
