#!/bin/bash


for bench in "100" "500" "1000" "1500" "2000" "2500" 
do
    echo $bench
    for i in `seq 10`
    do
	./pycket-c trace-benches/mergesort.rkt $bench  >> merge${bench}
    done
done
exit 0 
