#ifndef extraResource_H_
#define extraResource_H_
#include "extraResource.h"

using namespace std;
extraResource::extraResource(string datapath)
{
    if (datapath.length() < 2)
    {
        return;
    }
    string anchorPath = datapath + "anchorProbFile_all";
    ifstream infile(anchorPath.c_str());
    util utils;
    if(! infile)
    {
        cout << "Error openning: " << anchorPath << "\n";
    }
    else
    {
        string lineStr;
        while (getline(infile,lineStr))
        {
            double prob;
            string gram;
            istringstream iss(lineStr);
            iss >> prob;
// version 2: prob[tab]gram
            getline(iss, gram);
            gram = utils.trimStr(gram);
            wikiMap.insert(pair<string, double>(gram, prob));
        }
        infile.close();
    }
    cout << utils.getTime() << " grams' wikiProb are loaded. Items: " << wikiMap.size();

}

void extraResource::loadMSGram(string datapath, string timeStr)
{
    if (datapath.length() < 2)
    {
        return;
    }
    string gramPath = datapath + "qngrams_prob_jan" + timeStr;
    cout << "# Loading grams msprob from " << gramPath << endl;
    ifstream infile(gramPath.c_str());
    util utils;
    if(! infile)
    {
        cout << "Error openning: " << gramPath << "\n";
    }
    else
    {
        unigramMap.clear();
        twogramMap.clear();
        threegramMap.clear();
        fourgramMap.clear();
        fivegramMap.clear();
        string lineStr;
        while (getline(infile,lineStr))
        {
            double prob;
            string gram;
            istringstream iss(lineStr);
            iss >> prob;
// version 2: prob[tab]gram
            getline(iss, gram);
            gram = utils.trimStr(gram);
            int gramLen = utils.strToVector(gram).size();
            if(gramLen == 1){
                unigramMap.insert(pair<string, double>(gram, prob));
            }
            if(gramLen == 2){
                twogramMap.insert(pair<string, double>(gram, prob));
            }
            if(gramLen == 3){
                threegramMap.insert(pair<string, double>(gram, prob));
            }
            if(gramLen == 4){
                fourgramMap.insert(pair<string, double>(gram, prob));
            }
            if(gramLen == 5){
                fivegramMap.insert(pair<string, double>(gram, prob));
            }
        }
        infile.close();
        cout << utils.getTime() << " unigrams' prob are loaded. Items: " << unigramMap.size();
        cout << utils.getTime() << " two-grams' prob are loaded. Items: " << twogramMap.size();
        cout << utils.getTime() << " three-grams' prob are loaded. Items: " << threegramMap.size();
        cout << utils.getTime() << " four-grams' prob are loaded. Items: " << fourgramMap.size();
        cout << utils.getTime() << " five-grams' prob are loaded. Items: " << fivegramMap.size();
    }
}

void extraResource::loadAll(string datapath)
{
    if (datapath.length() < 2)
    {
        return;
    }
    util utils;
    DIR* dirp;
    struct dirent* direntp;
    dirp = opendir((char*)datapath.c_str());
    if(dirp != NULL)
    {
        for(;;)
        {
            direntp = readdir(dirp);
            if(direntp == NULL) break;
            string dname = direntp->d_name;
            if(dname == "."){ continue; }
            if(dname == ".."){ continue; }
            string subFileName = datapath+dname;
            ifstream infile(subFileName.c_str());
            if(! infile)
            {
                cout << "Error openning: " << subFileName << "\n";
            }
            else
            {
                map<string, double> probHash;
                string lineStr;
///*
                while (getline(infile,lineStr))
                {
                    double prob;
                    string gram;
                    istringstream iss(lineStr);
                    iss >> prob;
// version 1: prob[space]gram
/*
                    getline(iss, gram);
                    gram = utils.toLower(gram);
                    gram = lineStr.substr(lineStr.find('\t')+1, lineStr.length());
*/
// version 2: prob[tab]gram
                    getline(iss, gram);
                    gram = utils.trimStr(gram);
                    probHash.insert(pair<string, double>(gram, prob));
//                    cout << prob << "\t" << gram.length() << " #" << gram << "#" << endl;
                }
//*/
                infile.close();
                if (dname.find("anchorProbFile") != string::npos)
                {
                    wikiMap.insert(probHash.begin(), probHash.end());
                    cout << utils.getTime() << " grams' wikiProb are loaded. Items: " << wikiMap.size();
                }
                if (dname.find("gram1_prob") != string::npos)
                {
                    unigramMap.insert(probHash.begin(), probHash.end());
                    cout << utils.getTime() << " unigrams' prob are loaded. Items: " << unigramMap.size();
                }
                if (dname.find("gram2_prob") != string::npos)
                {
                    twogramMap.insert(probHash.begin(), probHash.end());
                    cout << utils.getTime() << " two-grams' prob are loaded. Items: " << twogramMap.size();
                }
                if (dname.find("gram3_prob") != string::npos)
                {
                    threegramMap.insert(probHash.begin(), probHash.end());
                    cout << utils.getTime() << " three-grams' prob are loaded. Items: " << threegramMap.size();
                }
                if (dname.find("gram4_prob") != string::npos)
                {
                    fourgramMap.insert(probHash.begin(), probHash.end());
                    cout << utils.getTime() << " four-grams' prob are loaded. Items: " << fourgramMap.size();
                }
                if (dname.find("gram5_prob") != string::npos)
                {
                    fivegramMap.insert(probHash.begin(), probHash.end());
                    cout << utils.getTime() << " five-grams' prob are loaded. Items: " << fivegramMap.size();
                }
                cout << " from file: " << subFileName << endl;
            }
        }
    }
}

extraResource::~extraResource(void)
{
}

int extraResource::getWikiGramNum()
{
    return wikiMap.size();
}

double extraResource::getWikiProb(string gram)
{
    if (wikiMap.find(gram) != wikiMap.end())
        return wikiMap.at(gram);
    return 0;
}

double extraResource::getMsProb(string gram, int wordNum)
{
    try
    {
        if (wordNum == 1)
        {
            return unigramMap.at(gram);
        }
        else if(wordNum == 2)
        {
            return twogramMap.at(gram);
        }
        else if(wordNum == 3)
        {
            return threegramMap.at(gram);
        }
        else if(wordNum == 4)
        {
            return fourgramMap.at(gram);
        }
        else if(wordNum == 5)
        {
            return fivegramMap.at(gram);
        }
        else
        {
            cout << "Error when get ms prob: wordNum invalid with number: " << wordNum << endl;
            return 0.0;
        }
    }
    catch (const out_of_range& oor)
    {
        cout << "Error when getting ms prob! Gram not existed: #" << gram << "# WordNum:" << wordNum << endl;
        return 0.0;
    }
}

map<string, double> extraResource::getWikiMap()
{
    return wikiMap;
}
map<string, double> extraResource:: getGramMap(int gramLen)
{
    if (gramLen == 1)
    {
        return unigramMap;
    }
    else if(gramLen == 2)
    {
        return twogramMap;
    }
    else if(gramLen == 3)
    {
        return threegramMap;
    }
    else if(gramLen == 4)
    {
        return fourgramMap;
    }
    else if(gramLen == 5)
    {
        return fivegramMap;
    }
}
#endif
