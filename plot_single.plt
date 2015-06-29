f(x) = a*x + b
fit f(x) 'whole_program.dat' via a,b
set term png size 1920,1080
set output 'single.png'
plot 'whole_program.dat' using 1:2, f(x)

