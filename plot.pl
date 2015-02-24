set style line 1 lc rgb '#0060ad' lt 1 lw 2 pt 7 ps 1.5 
plot 'results.plt' with linespoints ls 1
set term png
set output "simple.png"
replot
