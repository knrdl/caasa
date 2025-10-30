FROM node:lts-alpine AS client_builder

WORKDIR /app

COPY client/package.json .
COPY client/package-lock.json .

RUN npm install

COPY client .

RUN npm run check && \
    npm run build


FROM python:3.13.9-alpine3.22

ENV PYTHONUNBUFFERED=TRUE

WORKDIR /app

COPY server .

RUN apk --no-cache update && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 8080/tcp

CMD uvicorn main:app --host 0.0.0.0 --port 8080 --log-level info

COPY --from=client_builder /app/dist /www

