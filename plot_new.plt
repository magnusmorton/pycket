set term png enhanced
set output "combined.png"
set ylabel "Time (microseconds)"
set xlabel "Predicted cost"

set key off
set title "CM1 for all generated benchmarks "
set xrange [0:1400]
set yrange [0:50]
f1(x) = a1*x+ b1
f2(x) = a2*x+ b2
f3(x) = a3*x+ b3
filenames = "vecsetonly vectgtlt vectgtlt_random"

fit f1(x) "vecsetonly.plt" using 2:1  via a1, b1

fit f2(x) "vectgtlt.plt" using 2:1 via a2, b2

fit f3(x) "vectgtlt_random.plt" using 2:1 via a3, b3
plot "vecsetonly.plt" using 2:1, "vectgtlt.plt" using 2:1, "vectgtlt_random.plt" using 2:1, f1(x), f2(x), f3(x)

