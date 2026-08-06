VBM = 12.82469624

set terminal pngcairo size 1000,800
set output "diamond_hse06.png"

set style data dots
set nokey

y1 = -10
y2 = 15
gap = 5.25714969
set xrange [0:10.66892]
set yrange [y1 : y2]

set arrow from graph 0, first 0 to graph 1, first 0 nohead lc rgb "black" lw 1
set arrow from graph 0, first gap to graph 1, first gap nohead lc rgb "black" lw 1

set arrow from  1.75891, y1 to  1.75891,  y2 nohead
set arrow from  2.63836, y1 to  2.63836,  y2 nohead
set arrow from  3.26023, y1 to  3.26023,  y2 nohead
set arrow from  5.12584, y1 to  5.12584,  y2 nohead
set arrow from  6.64910, y1 to  6.64910,  y2 nohead
set arrow from  7.72620, y1 to  7.72620,  y2 nohead
set arrow from  8.34807, y1 to  8.34807,  y2 nohead
set arrow from  9.59181, y1 to  9.59181,  y2 nohead

set xtics ("Γ"  0.00000,"X"  1.75891,"W"  2.63836,"K"  3.26023,"Γ"  5.12584,"L"  6.64910,"U"  7.72620,"W"  8.34807,"L"  9.59181,"K" 10.66892)

plot "diamond_band.dat" using 1:($2 - VBM) with lines lw 1 lc black
