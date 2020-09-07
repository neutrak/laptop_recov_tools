#!/bin/bash

cd /home/guest/programs/laptop_recov_tools/campics/

while [ 1 ]
do
	filename="pic_$(date +"%FT%TZ")"
	
	#use mplayer to capture an image from the webcam
	mplayer -vo jpg -frames 4 tv://
	rm 0000000{1,2,3}.jpg
	mv "00000004.jpg" "$filename.jpg"
	
	#use ffmpeg to capture an image from the webcam
#	ffmpeg -f video4linux2 -i /dev/video0 -vframes 1 "$filename.jpg"
	
	#take another capture every 15 minutes
	sleep $((60*15))
done


