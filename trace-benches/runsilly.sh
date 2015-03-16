#!/bin/bash


for bench in  "100000" 

do
    echo $bench
    for i in `seq 10`
    do
	(perf stat ./pycket-c trace-benches/sumupto_silly.rkt $bench)  &>> sumupto_silly${bench}
    done
done
exit 0 
