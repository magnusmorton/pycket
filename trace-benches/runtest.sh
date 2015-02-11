#!/bin/bash


for bench in "1000" "10000" "100000" "1000000" "10000000"

do
    echo $bench
    for i in `seq 10`
    do
	./pycket-c trace-benches/sumupto.rkt $bench  >> sumupto${bench}
    done
done
exit 0 
