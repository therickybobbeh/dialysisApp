# ---------- Stage 1: Build Angular app ----------
FROM node:18 as builder
WORKDIR /app

COPY package*.json ./
RUN npm install
RUN npm install -g @angular/cli

COPY . .
RUN ng build --configuration=production

# ---------- Stage 2: Final NGINX stage ----------
FROM nginx:latest
RUN chmod 644 /etc/nginx/conf.d/default.conf
COPY ./nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist/dialysis-app/browser /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]