FROM nginx:1.25-alpine

# Default konfiguratsiyani o'chirish
RUN rm /etc/nginx/conf.d/default.conf

# Yangi konfiguratsiyani ko'chirish
COPY default.conf /etc/nginx/conf.d/
