FROM python:3.11
WORKDIR /web
COPY requirements.txt /web/requirements.txt
COPY migrations /web/migrations
COPY alembic.ini /web/alembic.ini
RUN pip3 install --no-cache-dir -r /web/requirements.txt
COPY  app  /web/app
CMD ["alembic", "revision", "--autogenerate"]
CMD ["alembic", "upgrade", "head"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

