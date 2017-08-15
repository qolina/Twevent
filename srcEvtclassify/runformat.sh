#binary threshold
i=0.0001
#whether use binary
sign=unbinary
#suffix of outputfile name
suffix=real
#positive set

pnum=0
#python arfFormatData.py -t -1 -s1 All -s2 $suffix -l libsvm -p $pnum -lex -tdt
#python arfFormatData.py -s1 All_norm_pos -l libsvm -p $pnum
python arfFormatData.py -s1 All_norm_mpos -l libsvm 
#python arfFormatData.py -s1 All_lex_pos -l libsvm -p $pnum -lex
#python arfFormatData.py -s1 All_lex_mpos -l libsvm -lex

#featureSet = ["01mue", "02seg", "03edg", "04sve", "05dfe", "06udf", "07rtm", "08men", "09rep", "10url", "11fav", "12tag", "13pst"]
