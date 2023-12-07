# Use an official Node runtime as a parent image
FROM node:14
RUN apt-get update

WORKDIR /usr/src/frontend

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000
CMD ["./startup.sh"]