FROM ubuntu:22.04

# Install dependencies non-interactively
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    python3 \
    python3-docutils \
    python3-scipy \
    gnuradio \
    tshark \
    # Dependencies for gr-gsm from https://osmocom.org/projects/gr-gsm/wiki/Installation#Debbian-based-distributions-Debian-Testing-Ubuntu-1604-Kali-Rolling-Edition
    cmake \
    autoconf \
    libtool \
    pkg-config \
    build-essential \
    libcppunit-dev \
    swig \
    doxygen \
    liblog4cpp5-dev \
    gnuradio-dev \
    #liborc-dev \
    libosmocore-dev \
    gr-osmosdr \
    # Required to clone gr-gsm
    ca-certificates \
    git \
    # Required to use the host timezone in the container
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Clone gr-gsm \
RUN git clone https://github.com/bkerler/gr-gsm.git \
    && cd gr-gsm \
    && mkdir build \
    && cd build \
    && cmake .. \
    && mkdir $HOME/.grc_gnuradio/ $HOME/.gnuradio/ \
    && make \
    && make install \
    && ldconfig \
    && cd ../.. \
    && rm -rf gr-gsm

COPY gsm-monitor /gsm-monitor
RUN chmod +x /gsm-monitor
RUN mkdir /output
#RUN apt update && apt install nano
ENTRYPOINT ["/gsm-monitor"]
