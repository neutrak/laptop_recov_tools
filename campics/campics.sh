#!/bin/bash

cd /home/guest/programs/campics/

n=0

while [ 1 ]
do
	#don't over-write existing files
	while [ -f "pic_${n}.png" ]
	do
		n=$(($n+1))
	done
	
	mplayer -vo png -frames 4 tv://
	rm 0000000{1,2,3}.png
	mv "00000004.png" "pic_${n}.png"
	sleep $((60*15))
	
	n=$(($n+1))
done


