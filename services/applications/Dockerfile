# syntax=docker/dockerfile:1.4
FROM django-base

WORKDIR /app
COPY . /app

EXPOSE 8009
CMD ["python", "manage.py", "runserver", "0.0.0.0:8009"]
