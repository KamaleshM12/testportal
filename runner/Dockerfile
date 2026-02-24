FROM debian:12-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jdk-headless \
    python3 \
    python3-pip \
    build-essential \
    g++ \
    wget \
    ca-certificates \
    git \
    procps \
    time \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash sandbox
WORKDIR /workspace
RUN chown sandbox /workspace
USER sandbox
ENV PATH="/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:$PATH"
CMD ["/bin/bash"]
