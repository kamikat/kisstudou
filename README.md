Introduction
============

Kisstudou is a python implementation of the flvcd.com client

Kisstodou has not yet been tested under windows, if you encountered
an error, please report in the issue list. Fix should be available 
in a few days.

**Automatic merging of sliptted clips has not yet been developed**. 
Refer to another repository 
[FLVCopycat](https://github.com/hanenoshino/FLVCopycat)
for this function

Installation
============

Kisstudou depend on Python 2.7 and PyQuery

Using following code to install pyquery

    python-pip install pyquery

Then, put the kisstudou script to your PATH

Usage
=====

Using the following command

    kisstudou --help

If you would like to download an album from bilibili,
create the following script

    #!/bin/bash

    for ((i=1;i<=$2;i++))
    do
    echo "http://www.bilibili.tv/video/$1/index_$i.html"
    done

and run the kisstudou with

    ./bilibili avXXXXXXX 13 | xargs -n1 kisstudou -d

in which 13 is the total part count of the video.

If you would like to limit the download speed, use `-O`
to pass parameter to `wget`

    kisstudou -O "--limit-rate=150k" [url]

