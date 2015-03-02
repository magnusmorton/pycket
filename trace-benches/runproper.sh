#!/bin/bash


for bench in  "10000" "100000" "1000000"

do
    echo $bench
    for i in `seq 10`
    do
	(perf stat ./pycket-c trace-benches/sumupto-proper.rkt $bench)  &>> sumupto-proper${bench}
    done
done
exit 0 
