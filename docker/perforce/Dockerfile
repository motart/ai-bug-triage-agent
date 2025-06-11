FROM ubuntu:22.04

ENV P4PORT=1666 \
    P4D_VERSION=r23.2 \
    P4ROOT=/opt/perforce \
    P4USER=admin \
    P4PASS=admin

RUN apt-get update \
    && apt-get install -y wget ca-certificates \
    && mkdir -p ${P4ROOT} \
    && useradd -m perforce \
    && chown perforce:perforce ${P4ROOT}

RUN wget -q https://cdist2.perforce.com/perforce/${P4D_VERSION}/bin.linux26x86_64/p4d -O /usr/local/bin/p4d \
    && wget -q https://cdist2.perforce.com/perforce/${P4D_VERSION}/bin.linux26x86_64/p4 -O /usr/local/bin/p4 \
    || (echo "Failed to download p4 binaries. Ensure the URL is correct and accessible." && exit 1) \
    && chmod +x /usr/local/bin/p4d /usr/local/bin/p4

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER perforce
WORKDIR ${P4ROOT}
EXPOSE ${P4PORT}

ENTRYPOINT ["/entrypoint.sh"]
CMD []
