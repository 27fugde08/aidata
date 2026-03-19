FROM node:18-alpine

WORKDIR /app

# Add /app/node_modules/.bin to PATH
ENV PATH /app/node_modules/.bin:$PATH

COPY package*.json ./

# Clean install dependencies
RUN npm install

# Copy source code
COPY . .

# Next.js telemetry disable for performance
ENV NEXT_TELEMETRY_DISABLED 1

EXPOSE 3000

# Use npx to ensure the local next binary is used, or npm run dev
CMD ["npm", "run", "dev"]
