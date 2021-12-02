FROM node:lts-alpine AS client_builder

WORKDIR /app

COPY client/package.json .
COPY client/package-lock.json .

RUN npm install

COPY client .

RUN npm run build


FROM python:3.9-slim

WORKDIR /app

RUN pip install --upgrade --no-cache-dir starlette uvicorn[standard] aiohttp aiodocker

EXPOSE 8080/tcp

CMD uvicorn main:app --host 0.0.0.0 --port 8080 --log-level info

COPY --from=client_builder /app/public /www
COPY server .
