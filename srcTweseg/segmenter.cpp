#ifndef segmenter_H_
#define segmenter_H_
#include "segmenter.h"

typedef pair<vector<string>, double> PAIR;
using namespace std;

segmenter::segmenter(void)
{
}

segmenter::~segmenter(void)
{
}

bool sortByVal(const PAIR &x, const PAIR &y)
{
    return (x.second > y.second); // descending
}


// u is maximum length of a segment s (num of words)
// e : top e element of segmentation Set is kept for segment s
map <string, int> segmenter::getNgram(vector<string> tweet, int u, int e)
{
    bool getNgramDebug = false;
    util utils;
    map <string, int> ngramMap; // ngram:leng;
    string tweetStr = utils.vectorToStr(tweet, ' ');
    if (getNgramDebug)
    {
        cout << "***" << tweetStr << endl;
    }

    int l = tweet.size();
    for (int i = 0; i < l; i ++)
    {
        vector<string> s_i (tweet.begin(), tweet.begin() + i + 1);
        string siStr = utils.vectorToStr(s_i, ' ');
        if (i < u)
        {
            ngramMap.insert(pair<string, int>(siStr, s_i.size()));
            if (getNgramDebug)
            {
                cout << "si # " << siStr << endl;
            }
        }

        for (int j = 0; j < i; j ++)
        {
            if ((i-j) <= u)
            {
                vector<string> s_i2(s_i.begin() + j + 1, s_i.end());
                string si2Str = utils.vectorToStr(s_i2, ' ');
                if (getNgramDebug)
                {
                    cout << "si2# " << si2Str << endl;
                }
                ngramMap.insert(pair<string, int>(si2Str, s_i2.size()));
            }
        }
    }
    if (getNgramDebug)
    {
        cout << "***************************************" << endl;
    }
    return ngramMap;
}

double CFunc(vector<string> seg, extraResource& resource)
{
	double l = 0.0;
	double scpVal = 0.0, ngramProb = 0.0, wikiProb = 0.0;
    double score = 0.0;
    util utils;
    string segStr = utils.vectorToStr(seg, ' ');
    wikiProb = resource.getWikiProb(segStr);
    wikiProb = exp(wikiProb);
    ngramProb = resource.getMsProb(segStr, seg.size());

    ngramProb = pow(10.0, ngramProb);
	if (seg.size() == 1)
    {
        l = 1.0 ;
        scpVal = 2 * log10(ngramProb);
//        score = l * wikiProb * utils.sigmoid(scpVal);
        score = l * wikiProb * 2 * utils.sigmoid(scpVal);
//        cout << segStr << "(l|wiki|ngramProb|scp): ";
//        cout << l << "\t" << wikiProb << "\t" << ngramProb << "\t";
//        cout << scpVal << endl;
    }
    else
    {
		l = (seg.size()-1)*1.0 / seg.size();
        // scpval
        scpVal = ngramProb * ngramProb;
        double tempScore = 0.0;
        for (int i = 0; i <= seg.size()-2; i ++)
        {
            string seg1Str = utils.vecToStr(seg, ' ', 0, i+1);
            string seg2Str = utils.vecToStr(seg, ' ', i+1, seg.size());
            double seg1Prob = resource.getMsProb(seg1Str, i+1);
            double seg2Prob = resource.getMsProb(seg2Str, seg.size()-i-1);
            seg1Prob = pow(10.0, seg1Prob);
            seg2Prob = pow(10.0, seg2Prob);
            tempScore += seg1Prob * seg2Prob;
        }
        tempScore = tempScore / (seg.size()-1);
        scpVal = log10(scpVal / tempScore);

//        score = l * wikiProb * utils.sigmoid(scpVal);
        score = l * wikiProb * 2 * utils.sigmoid(scpVal);
	}
//    cout << segStr << "(l|wiki|ngramProb|scp|score): ";
//    cout << l << "\t" << wikiProb << "\t" << ngramProb << "\t" << scpVal << "\t";
//    cout << score << endl;
	return score;
}

pair<vector<string>, double> segmenter::segment(vector<string> tweet, int u, int e, extraResource& resource)
{
    bool segDebug = false;
    util utils;
    string tweetStr = utils.vectorToStr(tweet, ' ');
    if (segDebug)
    {
        cout << "***" << tweetStr << endl;
    }
    vector<vector<pair<vector<string>, double> > > SegSet;
    int l = tweet.size();
    for (int i = 0; i < l; i ++)
    {
        vector<pair<vector<string>, double> > segSet_i;
        vector<string> s_i (tweet.begin(), tweet.begin() + i + 1);
        string siStr = utils.vectorToStr(s_i, ' ');
//        if (segDebug)
//        {
//            cout << "# " << siStr << endl;
//        }
        if (i < u)
        {
            double value = CFunc(s_i, resource);
            vector<string> s_iVec;
            s_iVec.push_back(siStr);
            segSet_i.push_back(pair<vector<string>, double>(s_iVec, value));
            if (segDebug)
            {
                cout << "Added s_i: " << utils.vectorToStr(s_iVec, ' ') << "# " << value << endl;
            }
        }

        for (int j = 0; j < i; j ++)
        {
            if ((i-j) <= u)
            {
                vector<string> s_i1(s_i.begin(), s_i.begin() + j + 1);
                vector<string> s_i2(s_i.begin() + j + 1, s_i.end());
                double si2Val = CFunc(s_i2, resource);
                string si2Str = utils.vectorToStr(s_i2, ' ');
//                if (segDebug)
//                {
//                    cout << "# " << si2Str << endl;
//                }
                vector<pair<vector<string>, double> > segSet_j;
                segSet_j = SegSet.at(j);
                vector<pair<vector<string>, double> >::iterator iter;
                for (iter = segSet_j.begin(); iter != segSet_j.end(); iter++)
                {
                    vector<string> s_j = iter->first;
                    double sjVal = iter->second;
                    vector<string> newS = s_j;
                    newS.push_back(si2Str);
                    double newSVal = sjVal + si2Val;
                    segSet_i.push_back(pair<vector<string>, double>(newS, newSVal));
                    if (segDebug)
                    {
                        cout << "Added s_j + s_i2: " << utils.vectorToStr(s_j, '|') << '|' << si2Str << "# " << newSVal << endl;
                    }
                }
            }
            if (segDebug)
            {
                cout << "##Before sort segSet" << i <<" Num: " << segSet_i.size() << endl;
                vector<pair<vector<string>, double> >::iterator iter;
                for (iter = segSet_i.begin(); iter != segSet_i.end(); iter ++)
                {
                    cout << utils.vectorToStr(iter->first, '|');
                    cout << " :" << iter->second << endl;
                }
                cout << "############" << endl;
            }
            // sort s_i and keep top e segs
            sort(segSet_i.begin(), segSet_i.end(), sortByVal);
            //qsort(segSet_i.begin(), segSet_i.size(), sizeof(PAIR), sortByVal);

            int segSeti_Num = segSet_i.size();
            if(segSeti_Num > e)
            {
                segSet_i.erase(segSet_i.begin() + e, segSet_i.end());
            }
        }

        if (segDebug)
        {
            cout << "##After sort segSet" << i <<" Num: " << segSet_i.size() << endl;
            vector<pair<vector<string>, double> >::iterator iter;
            for (iter = segSet_i.begin(); iter != segSet_i.end(); iter ++)
            {
                cout << utils.vectorToStr(iter->first, '|');
                cout << " :" << iter->second << endl;
            }
            cout << "***************************************" << endl;
        }
        SegSet.push_back(segSet_i);
    }
    vector<pair<vector<string>, double> > segSet_l;
    segSet_l = SegSet.back();
/*    
    if (segDebug)
    {
        cout << "segmentation Num: " << segSet_l.size() << endl;
        vector<pair<vector<string>, double> >::iterator iter;
        for (iter = segSet_l.begin(); iter != segSet_l.end(); iter ++)
        {
            cout << utils.vectorToStr(iter->first, '|');
            cout << " :" << iter->second << endl;
        }
        cout << "***************************************" << endl;
    }
*/
    return segSet_l.front();
}
#endif

