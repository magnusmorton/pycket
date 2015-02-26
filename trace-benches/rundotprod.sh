#!/bin/bash


for bench in  "7500" "100000"

do
    echo $bench
    for i in `seq 10`
    do
	./pycket-c trace-benches/dotproduct.rkt $bench  >> dot${bench}
    done
done
exit 0 
