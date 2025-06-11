FROM ubuntu:22.04

ENV P4PORT=1666 \
    P4D_VERSION=r23.2 \
    P4ROOT=/opt/perforce

RUN apt-get update \
    && apt-get install -y wget ca-certificates \
    && mkdir -p ${P4ROOT} \
    && useradd -m perforce \
    && chown perforce:perforce ${P4ROOT}

RUN wget -q https://cdist2.perforce.com/perforce/${P4D_VERSION}/bin.linux26x86_64/p4d -O /usr/local/bin/p4d \
    || (echo "Failed to download p4d. Ensure the URL is correct and accessible." && exit 1) \
    && chmod +x /usr/local/bin/p4d

USER perforce
WORKDIR ${P4ROOT}
EXPOSE ${P4PORT}

CMD ["p4d", "-r", "/opt/perforce", "-p", "1666", "-d", "--foreground"]
