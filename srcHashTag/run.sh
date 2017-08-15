if [ "$#" -ne 1 ]; then
    echo "Error"
    exit 1
fi

#python process.py $1 $1.weight.prefix.case $1.weight.suffix.case weight
#python process.py $1 $1.unweight.prefix.case $1.unweight.suffix.case unweight

#python process.py $1 $1.weight.prefix.rankbyKey $1.weight.suffix.rankbyKey weight
#python process.py $1 $1.unweight.prefix.rankbyKey $1.unweight.suffix.rankbyKey unweight


python process.py $1 $1.weight.prefix.igcase $1.weight.suffix.igcase weight
#python process.py $1 $1.unweight.prefix.igcase $1.unweight.suffix.igcase unweight

#python process.py $1 $1.weight.prefix.rankbyKey.igcase $1.weight.suffix.rankbyKey.igcase weight
#python process.py $1 $1.unweight.prefix.rankbyKey.igcase $1.unweight.suffix.rankbyKey.igcase unweight
