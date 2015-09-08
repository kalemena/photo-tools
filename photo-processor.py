#!/usr/bin/env python

# Scroll through specified folder and rename photos based on EXIF metadata.
# Rename videos based on file time.
# Duplicate MOV MJPEG video transcoded in x264 lossless.
#
# Example usage
# ./photo-processor.py -s <source folder>

# Example manual convert video
# convert rose.jpg -resize 50% rose.png
# avidemux2_cli --nogui --load file.MOV --video-codec x264 --save file.AVI

import os
import sys
import optparse
import pyexiv2 as pe
import time
import stat

class NoFile(Exception):

    def __init__(self, msg):
        self.msg = msg


def custom_listdir(path):
    """
    Returns the content of a directory by showing directories first
    and then files by ordering the names alphabetically
    """
    dirs = sorted([d for d in os.listdir(path) \
        if os.path.isdir(path + os.path.sep + d)])
    dirs.extend(sorted([f for f in os.listdir(path) \
        if os.path.isfile(path + os.path.sep + f)]))

    return dirs


def processVideo(srcfile):
    froot, ext = os.path.splitext(srcfile)
    print '> ', srcfile
    dstfile = '%s%s' % (froot, '.AVI')
    print '> ', dstfile
    os.system("avidemux2_cli --nogui --load %s --video-codec x264 --save %s" \
        % (srcfile, dstfile))

def renameRaw(folder, srcfile, dstfile):
    print '>  ', dstfile, ' <--- ', srcfile
    dstfile = os.path.join(folder, dstfile)
    if(os.path.exists(dstfile)):
        froot, ext = os.path.splitext(srcfile)
        froot += 'A'
        dstfile = os.path.join(froot, dstfile)

    os.rename(srcfile, dstfile)

    froot, ext = os.path.splitext(dstfile)        #get the extension
    if ext.lower() == '.mov':
        processVideo(dstfile)


def renamePhoto(srcfile):
    # print "> Photo is: '%s'" % srcfile
    metadata = pe.ImageMetadata(srcfile)
    metadata.read()
    date = metadata['Exif.Image.DateTime']

    # Calculate new image name
    froot, ext = os.path.splitext(srcfile)
    dstfile = '%04i%02i%02i_%02i%02i%02i%s' % \
            (date.value.year, date.value.month, date.value.day, \
             date.value.hour, date.value.minute, date.value.second, \
             ext.upper())

    renameRaw(os.path.dirname(srcfile), srcfile, dstfile)


def renameFile(srcfile):
    # print "> File is: '%s'" % srcfile
    file_stats = os.stat(srcfile)

    # Calculate new image name
    dstfile = time.strftime("%Y%m%d_%H%M%S", \
        time.localtime(file_stats[stat.ST_MTIME]))

    froot, ext = os.path.splitext(srcfile)        #get the extension
    dstfile = dstfile + ext.upper()

    renameRaw(os.path.dirname(srcfile), srcfile, dstfile)


def iterateRecursively(srcfolder):
    try:
        #test whether the folder passed exists, and the path is good
        if not os.path.exists(srcfolder):
            raise NoFile("Folder '%s' does not exist" % srcfolder)
        dname, fod_name = os.path.split(srcfolder)

        if not os.path.isdir(srcfolder):
            raise NoFile("'%s' is not a folder" % srcfolder)

        print ">>> Folder: '%s'" % srcfolder

        listing = custom_listdir(srcfolder) # os.listdir(srcfolder)

        # process the files
        for infile in listing:
            if not os.path.isdir(os.path.join(srcfolder, infile)):

                froot, ext = os.path.splitext(infile) #get the extension
                if ext.lower() == '.jpg':
                    try:
                        renamePhoto(os.path.join(srcfolder, infile))
                    except KeyError, err:
                        renameFile(os.path.join(srcfolder, infile))
                elif ext.lower() == '.mov' or ext.lower() == '.avi' or ext.lower() == '.mp4':
                    renameFile(os.path.join(srcfolder, infile))
                else:
                    print '>  ', infile, ' <--- UNKNOWN'

        # recurse the folders
        for infile in listing:
            if os.path.isdir(os.path.join(srcfolder, infile)):
                iterateRecursively(os.path.join(srcfolder, infile))

    except NoFile, err:
        print err.msg


if __name__ == '__main__':
    parser=optparse.OptionParser()
    parser.add_option('-s', '--source', dest='source',
                type="string",
                default="/home/clement/Images/tmp",
                help="Directory used to iterate recursively the pictures.")
    (options, args) = parser.parse_args()

    try:
        iterateRecursively(options.source)
    except:
        exc_info = sys.exc_info()
        print "unhandled exception: %s %s %s" \
            % (exc_info[0], exc_info[1], exc_info[2])

