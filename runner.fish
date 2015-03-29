#!/usr/local/bin/fish

rm output/*
for x in (seq 1 10  1500)
	sed s/Z/$x/ < trace-benches/generator.rkt.t > generated.rkt
	for i in (seq 10)
		./pycket-c generated.rkt 10000 10000 >> output/generated_all$x
	end

end
