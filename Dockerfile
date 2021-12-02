FROM node:lts-alpine AS client_builder

WORKDIR /app

COPY client/package.json .
COPY client/package-lock.json .

RUN npm install

COPY client .

RUN npm run build


FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install --yes build-essential && \
    pip install --upgrade pip && \
    pip install --upgrade --no-cache-dir starlette uvicorn[standard] aiohttp aiodocker && \
    apt-get purge build-essential && \
    apt-get autoremove --yes && \
    apt-get clean --yes && \
    rm -rf /var/lib/apt/lists/*
    

EXPOSE 8080/tcp

CMD uvicorn main:app --host 0.0.0.0 --port 8080 --log-level info

COPY --from=client_builder /app/public /www
COPY server .
