FROM nginx:latest

# Remover configuración por defecto y copiar la nuestra
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/nginx.conf
