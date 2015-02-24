#!/bin/bash


for bench in  `seq 10000 500 20000`
do
    echo $bench
    for i in `seq 10`
    do
	./pycket-c trace-benches/mergesort.rkt $bench  >> merge${bench}
    done
done
exit 0 
