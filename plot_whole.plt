set term png size 1920,1080
set output 'whole.png'
plot 'whole_program.dat' using 1:2:3  with labels point offset character 0,character 1 tc rgb "blue"

