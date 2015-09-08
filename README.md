# photo-tools
Tools used to sort and transcode pictures

# pre-requisits
* python
* libexiv2
* avidemux2
 
# usage

To rename all pictures based on EXIF metadata, then rename video, then duplicate MJPEG MOV video as x264 AVI:
$ ./photo-processor.py -s <source folder>
