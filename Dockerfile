FROM python:3.11-slim

ARG ENVIRONMENT
ARG PORT=8000
ENV ENVIRONMENT=$ENVIRONMENT


WORKDIR /app

#COPY requirements.txt .
COPY . .


RUN apt-get update && apt-get install -y vim \
    && pip install --no-cache-dir -r requirements.txt


EXPOSE $PORT

CMD if [ "$ENVIRONMENT" = "dev" ]; then \
    uvicorn main:app --host 0.0.0.0 --port $PORT --reload  --forwarded-allow-ips '*'; \
    else \
    gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind :$PORT --workers 1 --threads 8 --timeout 0 --forwarded-allow-ips="*"; \
    fi
