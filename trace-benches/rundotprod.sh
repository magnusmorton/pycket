#!/bin/bash


for bench in   10000 25000 75000 100000

do
    echo $bench
    for i in `seq 100`
    do
	(perf stat ./pycket-c trace-benches/dotproduct.rkt $bench)  &>> dot${bench}
    done
done
exit 0 
