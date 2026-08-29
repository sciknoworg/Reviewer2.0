FROM nginx:alpine

COPY . /usr/share/nginx/html
COPY docker-entrypoint.sh /docker-entrypoint.d/40-render-config.sh

RUN chmod +x /docker-entrypoint.d/40-render-config.sh \
    && rm -f /usr/share/nginx/html/Dockerfile /usr/share/nginx/html/docker-entrypoint.sh

ENV API_BASE_URL=http://localhost:8000

EXPOSE 80
