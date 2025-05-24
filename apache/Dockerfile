FROM httpd:2.4

# Habilitar los módulos de proxy en Apache
RUN sed -i 's/#LoadModule proxy_module/LoadModule proxy_module/' /usr/local/apache2/conf/httpd.conf \
 && sed -i 's/#LoadModule proxy_http_module/LoadModule proxy_http_module/' /usr/local/apache2/conf/httpd.conf \
 && sed -i 's/#Include conf\\/extra\\/httpd-vhosts.conf/Include conf\\/extra\\/httpd-vhosts.conf/' /usr/local/apache2/conf/httpd.conf

# Copiar archivo de configuración de Virtual Hosts
COPY httpd-vhosts.conf /usr/local/apache2/conf/extra/httpd-vhosts.conf
