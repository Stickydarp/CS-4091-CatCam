FROM node:20-slim

WORKDIR /app

COPY ./catCamFrontend /app

RUN npm install