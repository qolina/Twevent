# unsup method 1
#for i in $(seq 10 20)
#do
#    python eventFilterUnsup.py -1 All $i
#done


# unsup method 2
#for j in $(seq 1 16)
#do    
#    for i in $(seq 20 40)
#    do
#        python eventFilterUnsup.py -1 All $i $j
#    done
#done

# unsup method 3(unsupfilter.py)
#Usage: unsupfilter.py [-p pnum -f feaId -norm -sum -vote -d toDelFeas] -s suffixStr -n scoreThreshold

# vote threshold
#for i in $(seq 0 17)
#do
#    python unsupfilter.py -s musim -n $i -vote
#done

suffix="musim"
sfx2="normalize"
python unsupfilter.py -s $suffix -norm > out/out_norm_$suffix\_$sfx2
python unsupfilter.py -s $suffix -sum > out/out_sum_$suffix\_$sfx2
python unsupfilter.py -s $suffix -mlp > out/out_mlp_$suffix\_$sfx2
python unsupfilter.py -s $suffix -vote > out/out_vote_$suffix\_$sfx2

