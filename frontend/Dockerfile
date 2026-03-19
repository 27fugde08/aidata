FROM node:18-alpine

WORKDIR /app

COPY package*.json ./

# Clean install dependencies
RUN npm install

COPY . .

# Next.js telemetry disable for performance
ENV NEXT_TELEMETRY_DISABLED 1

EXPOSE 3000

CMD ["npm", "run", "dev"]
