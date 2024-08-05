FROM python:3.11.9@sha256:38b425945de90afd3c9159309bda02bef439a3331ee8b9f1a86b0edba328da4d

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

RUN playwright install-deps

RUN playwright install

COPY ./app /code/app

CMD ["fastapi", "run", "app/main.py"]
