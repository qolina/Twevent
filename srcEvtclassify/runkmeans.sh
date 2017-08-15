pnum=0
threshold=$1

sfx=norm_pos_0
#python kmeansfilter.py -p $pnum -s $sfx > out_kmeans_$sfx

sfx=norm_mpos
python kmeansfilter.py -s $sfx > out_kmeans_$sfx

sfx=lex_pos_0
#python kmeansfilter.py -p $pnum -s $sfx > out_kmeans_$sfx

sfx=lex_mpos
#python kmeansfilter.py -s $sfx > out_kmeans_$sfx

