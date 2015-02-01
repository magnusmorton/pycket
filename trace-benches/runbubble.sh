#!/bin/bash


for bench in "1000" "10000" "25000" "50000" "75000" "100000" 

do
    echo $bench
    for i in `seq 10`
    do
	PYPYLOG=jit-log-opt:logfile_bubble  ./pycket-c trace-benches/bubble.rkt $bench  >> bubble${bench}
    done
done
exit 0 
