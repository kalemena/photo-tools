FROM ubuntu:14.04

# add repos for avidemux 
RUN echo "deb http://www.deb-multimedia.org wheezy main non-free" >> /etc/apt/sources.list
RUN echo "deb http://www.deb-multimedia.org wheezy-backports main" >> /etc/apt/sources.list

RUN apt-get update -y; \
	apt-get install -y avidemux-cli python-pyexiv2; \
	apt-get clean; \
	rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*;

ADD [ "*.py", "/" ]

VOLUME /photos
VOLUME /dest

# CMD [ "/photo-processor.py -s /photos" ]
# CMD [ "/photo-filter.py -s <source folder> -d <destination folder>" ]
CMD ["/bin/bash"]
