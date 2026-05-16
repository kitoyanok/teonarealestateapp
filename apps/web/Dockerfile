FROM node:22-alpine AS build
WORKDIR /app

COPY package.json package-lock.json* ./
COPY apps/web/package.json apps/web/package.json
COPY apps/api/package.json apps/api/package.json
RUN npm install

COPY . .
RUN npm run build --workspace @estateflow/web

FROM nginx:1.27-alpine
WORKDIR /usr/share/nginx/html

COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/apps/web/dist ./

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
