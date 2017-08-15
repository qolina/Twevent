
if false; then
    outputSfx="del0413merge1415"
    delStr="4_13"
    python processData.py -c $delStr -in EventDataset_All_musim -o $outputSfx
    python processData.py -c $delStr -in EventTrainDataset_All_musim -o $outputSfx
    python processData.py -c $delStr -in EventTestDataset_All_musim -o $outputSfx
    python processData.py -c $delStr -in EventDevDataset_All_musim -o $outputSfx
fi

suffix="musim3"
sfx2="normalize"
if true; then
    for i in $(seq 1 14)
    do
        python processData.py -c $i -in data_$suffix -o del$i
    done
fi

