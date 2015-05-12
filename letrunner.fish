#!/usr/bin/env fish

rm output/*
for x in (seq 1 10  1500)
        echo $x
	set y (math "$x-1")
	sed -e s/X/$x/ -e s/Y/$y/ < trace-benches/arith.rkt.t > generated_let.rkt
	for i in (seq 10)
                echo $i
		./pycket-c generated_let.rkt 10000 10000 >> output/generated_let$x
	end

end
