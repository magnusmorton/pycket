#!/bin/bash


for bench in  `seq 10000 10000 100000`

do
    echo $bench
    for i in `seq 10`
    do
	(perf stat ./pycket-c trace-benches/crossproduct.rkt $bench)  >> dot${bench}
    done
done
exit 0 
