#!/bin/bash


for bench in  "10000" "100000" "1000000"

do
    echo $bench
    for i in `seq 10`
    do
	(perf stat ./pycket-c trace-benches/sumupto.rkt $bench)  &>> sumupto_silly${bench}
    done
done
exit 0 
