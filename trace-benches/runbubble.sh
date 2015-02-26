#!/bin/bash


for bench in "1000" "2500" "5000" "7500" "10000" "12500" "15000" "17500" "25000" "37500" "40000"  "50000" "75000" "100000" 

do
    echo $bench
    for i in `seq 10`
    do
	(perf stat ./pycket-c trace-benches/bubble.rkt $bench)  &>> bubble${bench}
    done
done
exit 0 
