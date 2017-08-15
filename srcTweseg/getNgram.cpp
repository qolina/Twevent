// tweetSegment.cpp : Defines the entry point for the console application.
//

#include "segmenter.h"
#include "Headers.h"
#include "util.h"

using namespace std;

int main()
{
    bool ngramsToFile = true;
    map<string, int> nGramsMap;
    util utils;
//    string datapath = "..//testData//";
    string datapath = "..//Data_hfmon//";
    string outputGramPath = datapath + "grams_qtwe//";
    
    cout << "Program starts at " << utils.getTime() << endl;

    int nullTweetNum = 0;
    // read files from datapath
    int lineIndex = 0;
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
            if(dname.find("tweetContentFile") != 0){
                continue;
            }
            string timeStr = dname.substr(dname.length()-2);
            cout << "Time Window: " + timeStr << endl;
            char* subFileName = (char*)(datapath+dname).c_str();
            cout << "Reading file: " << subFileName << endl;
            ifstream infile(subFileName);
            string gramPath = outputGramPath + "qngrams_jan" + timeStr;
            ofstream outfile(gramPath.c_str());
            cout << "writen to file: " << gramPath << endl;
            if(! infile)
            {
                cout << "Error openning: " << subFileName << "\n";
            }
            else
            {
                map<string, int> t_nGramsMap;
                string lineStr;
                // read file and load each line into lineStr
                while (getline(infile,lineStr))
                {
                    lineIndex += 1;
                    vector<string> tweet = utils.tweetStrToVec(lineStr);
                    segmenter twesegger;

                    string tweetIDStr = tweet.front();
                    tweet.erase(tweet.begin()); // erase tweetIDStr

                    if (tweet.size() == 0)
                    {
                        nullTweetNum += 1;
                       // cout << "###Null tweet" << lineStr << endl;
                        continue;
                    }
                    // to lower
                    tweet = utils.strToVector(utils.toLower(utils.vectorToStr(tweet,' ')));

                    // get ngram in tweet
                    if (ngramsToFile)
                    {
//                        cout << "tweetContent: " << utils.vectorToStr(tweet, ' ') << endl;
                        map<string, int> twe_ngramMap = twesegger.getNgram(tweet, 5, 5);
                        nGramsMap.insert(twe_ngramMap.begin(), twe_ngramMap.end());// statistic length of grams
                        t_nGramsMap.insert(twe_ngramMap.begin(), twe_ngramMap.end());// all grams in t
                    }
                    if (lineIndex % 100000 == 0)
                    {
                        cout << "### " << lineIndex << " tweets have been processed." << endl;
                    }
                }
                infile.close();
                map<string, int>::iterator iter;
                for (iter = t_nGramsMap.begin(); iter != t_nGramsMap.end(); iter ++)
                {
                    outfile << iter->first << endl;
                    outfile.flush();
                }
                outfile.close();
                cout << utils.getTime() << " " << t_nGramsMap.size() << " NGrams are writen into: " << gramPath << endl;
            }
        }
        closedir(dirp);
    }
    cout << "All tweet number: " << lineIndex << endl;
    cout << "Null tweet number: " << nullTweetNum << endl;
    cout << "### grams in hfmon: " << nGramsMap.size() << endl;

//	cout << "tweet n-grams:" << endl;
    map<string, int>::iterator iter;
    map<int, int> gramNumMap;
    for (iter = nGramsMap.begin(); iter != nGramsMap.end(); iter ++)
    {
//      cout << iter->second << ":" << iter->first << endl;
        if (gramNumMap.find(iter->second) != gramNumMap.end())
        {
            gramNumMap[iter->second] = gramNumMap.find(iter->second)->second + 1;
        }
        else
        {
            gramNumMap.insert(pair<int, int>(iter->second, 1));
        }

        if (iter->first[0] == '#')
        {
            cout << "#:" << iter->first << endl;
        }
    }
    cout << "tweet n-gram distribution:" << endl;
    map<int, int>::iterator gramNumIter;
    for (gramNumIter = gramNumMap.begin(); gramNumIter != gramNumMap.end(); gramNumIter ++)
    {
        cout << gramNumIter->first << ":" << gramNumIter->second << endl;
    }

    cout << "Program ends at " << utils.getTime() << endl;
    return 0;
}

