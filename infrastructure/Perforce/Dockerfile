FROM ubuntu:20.04

# Set environment variables
ENV P4PORT=1666 \
    P4USER=admin \
    P4PASSWD=Passw0rd123! \
    P4ROOT=/perforce-data \
    P4DEPOTS=/perforce-data/depots \
    DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
 && rm -rf /var/lib/apt/lists/*

# Add Perforce package repository
RUN wget -q https://package.perforce.com/perforce.pubkey -O /tmp/perforce.pubkey && \
    apt-key add /tmp/perforce.pubkey && \
    echo "deb http://package.perforce.com/apt/ubuntu focal release" > /etc/apt/sources.list.d/perforce.list && \
    apt-get update

# Install Helix Core (P4D)
RUN apt-get install -y helix-p4d

# Create Perforce data directory
RUN mkdir -p $P4ROOT $P4DEPOTS

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose Perforce port
EXPOSE 1666

# Set volumes for persistent storage
VOLUME ["/perforce-data"]

# Entrypoint to initialize and start P4D
ENTRYPOINT ["/entrypoint.sh"]
