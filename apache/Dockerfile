FROM httpd:2.4

COPY ./httpd.conf /usr/local/apache2/conf/httpd.conf
COPY ./httpd-vhosts.conf /usr/local/apache2/conf/extra/httpd-vhosts.conf

RUN echo "Include /usr/local/apache2/conf/extra/httpd-vhosts.conf" >> /usr/local/apache2/conf/httpd.conf

RUN apt-get update && apt-get install -y libapache2-mod-proxy-html libxml2-dev && \
    apt-get clean

RUN sed -i '/LoadModule proxy_module/s/^#//g' /usr/local/apache2/conf/httpd.conf && \
    sed -i '/LoadModule proxy_http_module/s/^#//g' /usr/local/apache2/conf/httpd.conf
