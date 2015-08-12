#!/bin/bash



for i in `seq 10`
do
    ./pycket-c trace-benches/matmul.rkt 1 >> matmulvecx1 
done

for i in `seq 10`
do
    ./pycket-c trace-benches/matmul.rkt 2 >> matmulvecx2 
done

for i in `seq 10`
do
    ./pycket-c trace-benches/matmul.rkt 4 >> matmulvecx4 
done

for i in `seq 10`
do
    ./pycket-c trace-benches/matmul.rkt 10 >> matmulvecx10 
done

exit 0 
