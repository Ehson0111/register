FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DEFAULT_TIMEOUT=120
ENV PIP_RETRIES=10
ENV PIP_INDEX_URL=http://pypi.tuna.tsinghua.edu.cn/simple
ENV PIP_TRUSTED_HOST="pypi.tuna.tsinghua.edu.cn pypi.org files.pythonhosted.org"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/databases

COPY requirements.docker.txt /app/requirements.docker.txt
RUN pip install --no-cache-dir --retries ${PIP_RETRIES} --timeout ${PIP_DEFAULT_TIMEOUT} -r /app/requirements.docker.txt

COPY . /app

EXPOSE 8009
CMD ["python", "manage.py", "runserver", "0.0.0.0:8009"]

