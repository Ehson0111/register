FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DEFAULT_TIMEOUT=120
ENV PIP_RETRIES=10

WORKDIR /app

RUN mkdir -p /app/databases

COPY requirements.docker.txt /app/requirements.docker.txt
RUN pip install --no-cache-dir --retries ${PIP_RETRIES} --timeout ${PIP_DEFAULT_TIMEOUT} -r /app/requirements.docker.txt

COPY . /app

EXPOSE 8006
CMD ["python", "manage.py", "runserver", "0.0.0.0:8006"]

