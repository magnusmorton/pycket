#!/bin/bash



for i in `seq 10`
do
    ./pycket-c trace-benches/matmul.rkt >> matmul 
done

exit 0 
