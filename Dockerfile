FROM python:3.11.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

RUN playwright install-deps

RUN playwright install

COPY ./app /code/app

CMD ["fastapi", "run", "app/main.py"]
