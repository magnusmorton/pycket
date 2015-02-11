#!/bin/bash


for bench in "100" "500" "1000" "1500" "2000" "2500" 
do
    echo $bench
    for i in `seq 10`
    do
	PYPYLOG=jit-log-opt:logfile_bubble  ./pycket-c trace-benches/bubble.rkt $bench  >> bubble${bench}
    done
done
exit 0 
