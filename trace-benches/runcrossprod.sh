#!/bin/bash


for bench in  `seq 10000 50000 1000000`

do
    echo $bench
    for i in `seq 2`
    do
	(perf stat ./pycket-c trace-benches/crossproduct.rkt $bench)  &>> cross${bench}
    done
done
exit 0 
