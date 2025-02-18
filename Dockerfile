FROM python:3.10-slim

COPY . /app

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["bash", "-c", "alembic upgrade head && python main.py"]