FROM python:3.11.9@sha256:a23661e4d5dacf56028a800d3af100397a99b120d0f0de5892db61437fd9eb6c

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

RUN playwright install-deps

RUN playwright install

COPY ./app /code/app

CMD ["fastapi", "run", "app/main.py"]
