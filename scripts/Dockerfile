FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y \
	&& apt-get install -y software-properties-common \
# Avidemux
	&& add-apt-repository ppa:ubuntuhandbook1/avidemux \
	&& apt-get install -y avidemux2.7-cli \
# py3exiv2
	&& add-apt-repository ppa:vincent-vandevyvre/vvv \
	&& apt-get install -y python3-exiv2 \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ADD [ "*.py", "/" ]

VOLUME /photos
VOLUME /dest

# CMD [ "/photo-processor.py -s /photos" ]
# CMD [ "/photo-filter.py -s <source folder> -d <destination folder>" ]
CMD ["/bin/bash"]
