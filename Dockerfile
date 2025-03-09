FROM node:lts-alpine AS client_builder

WORKDIR /app

COPY client/package.json .
COPY client/package-lock.json .

RUN npm install

COPY client .

RUN npm run build


FROM python:3.12.9-slim

ENV PYTHONUNBUFFERED=TRUE

WORKDIR /app

COPY server .

RUN apt-get update && \
    apt-get install --yes build-essential && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge --yes build-essential && \
    apt-get autoremove --yes && \
    apt-get clean --yes && \
    rm -rf /var/lib/apt/lists/*
    

EXPOSE 8080/tcp

CMD uvicorn main:app --host 0.0.0.0 --port 8080 --log-level info

COPY --from=client_builder /app/dist /www

