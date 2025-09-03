# Stage 1: Build stage
FROM node:18 as builder

WORKDIR /app

# Use corepack to enable and activate pnpm, then install dependencies
COPY package*.json ./
RUN corepack enable && corepack prepare pnpm@latest --activate && pnpm install

COPY . .

RUN pnpm run build

# Stage 2: Final stage
FROM nginx:1.21.0-alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
