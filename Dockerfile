FROM python:3.11.9@sha256:38b425945de90afd3c9159309bda02bef439a3331ee8b9f1a86b0edba328da4d

WORKDIR /code

RUN apt update && apt install -y cron

COPY updater-cron /etc/cron.d/

RUN chmod 0644 /etc/cron.d/updater-cron

RUN crontab /etc/cron.d/updater-cron

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

RUN playwright install-deps

RUN playwright install

COPY ./app /code/app

COPY ./start.sh /code/start.sh

RUN chmod +x /code/start.sh

CMD ["sh", "/code/start.sh"]
