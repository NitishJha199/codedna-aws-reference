FROM python:3.12-slim

WORKDIR /app

COPY src/order-api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/order-api/app ./app
COPY database/init.sql ./database/init.sql

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
