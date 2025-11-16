FROM node:20-slim

WORKDIR /app

COPY ./catCamFrontend /app

RUN npm install

EXPOSE 3000

CMD ["npm", "run", "dev"]