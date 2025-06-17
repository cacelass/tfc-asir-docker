FROM httpd:2.4

COPY ./httpd.conf /usr/local/apache2/conf/httpd.conf
COPY ./httpd-vhosts.conf /usr/local/apache2/conf/extra/httpd-vhosts.conf

RUN echo "Include /usr/local/apache2/conf/extra/httpd-vhosts.conf" >> /usr/local/apache2/conf/httpd.conf

RUN apt update && apt install -y apache2 libxml2-dev && apt clean && \
    a2enmod proxy proxy_http proxy_html xml2enc

RUN sed -i '/LoadModule proxy_module/s/^#//g' /usr/local/apache2/conf/httpd.conf && \
    sed -i '/LoadModule proxy_http_module/s/^#//g' /usr/local/apache2/conf/httpd.conf
