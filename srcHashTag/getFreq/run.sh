if [ "$#" -ne 1 ]; then
    echo "Error"
    exit 1
fi

#python process.py $1 $1.weight.prefix.case $1.weight.suffix.case weight
#python process.py $1 $1.unweight.prefix.case $1.unweight.suffix.case unweight

#python process.py $1 $1.weight.prefix.rankbyKey $1.weight.suffix.rankbyKey weight
#python process.py $1 $1.unweight.prefix.rankbyKey $1.unweight.suffix.rankbyKey unweight

#echo "Generating prefix/suffix..."
#python process.py $1 $1.weight.prefix.igcase $1.weight.suffix.igcase weight
#python process.py $1 $1.unweight.prefix.igcase $1.unweight.suffix.igcase unweight

#python process.py $1 $1.weight.prefix.rankbyKey.igcase $1.weight.suffix.rankbyKey.igcase weight
#python process.py $1 $1.unweight.prefix.rankbyKey.igcase $1.unweight.suffix.rankbyKey.igcase unweight


python reverse.py $1.weight.suffix.igcase $1.weight.suffix.igcase.reverse

for file in $1.weight.prefix.igcase $1.weight.suffix.igcase.reverse
do
    echo "Pruning $file"

    awk -F'\t' 'length($1)>2{print}' $file > $file.step1

    python pruning.py $file.step1 $file.step2

    awk -F'\t' '$2>=200{print}' $file.step2 > $file.step3

    sort -t'	' -k1 $file.step3 > $file.step4

#    python keepLongest.py $file.step4 $file.step5
    python keepShortest.py $file.step4 $file.step5
done

cp $1.weight.prefix.igcase.step5 $1.weight.prefix.result
python reverse.py $1.weight.suffix.igcase.reverse.step5 $1.weight.suffix.result
