FROM alpine:3.20
RUN apk add --no-cache bash git openssh-client ca-certificates \
    && rm -rf /var/cache/apk/* && \
    update-ca-certificates

# Install TruffleHog
RUN wget https://github.com/trufflesecurity/trufflehog/releases/download/v3.28.2/trufflehog_3.28.2_linux_amd64.tar.gz \ 
    && tar -xzf trufflehog_3.28.2_linux_amd64.tar.gz \
    && mv trufflehog /usr/bin/trufflehog \
    && rm trufflehog_3.28.2_linux_amd64.tar.gz
COPY entrypoint.sh /etc/entrypoint.sh
RUN chmod +x /etc/entrypoint.sh

# Install wrapper
RUN apk add --no-cache python3 py3-pip
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt
COPY wrapper.py /root/wrapper.py

ENTRYPOINT ["/etc/entrypoint.sh"]