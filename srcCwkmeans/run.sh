
if [ $# -ne 1 ]; then
    echo " Usage: sh run.sh data.libsvm"
    exit
fi

echo "-------------------------------------------------"
echo "Initiate..."
python kmeansfilter.py -if $1 -of $1.newLabel 

cp $1.newLabel $1.tmp

#for ((i=1;i<=5;i++))
for i in $(seq 1 15)
do
    echo "-------------------------------------------------"
    echo "Iteration $i..."
    cp $1.tmp $1.iter.$i
#    ./cw_binary_learn.exe -f 3 $1.iter.$i $1.iter.$i.model
    ./cw_binary_learn -f 3 $1.iter.$i $1.iter.$i.model
    python reweight.py $1.iter.$i.model $1.iter.$i $1.iter.$i.newWeight
    python kmeansfilter.py -if $1.iter.$i.newWeight -of $1.iter.$i.newWeight.newLabel -tl trueLabel.txt
    cp $1.iter.$i.newWeight.newLabel $1.tmp
done
