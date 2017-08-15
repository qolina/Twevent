#pragma once
#include "Headers.h"
#include "util.h"
using namespace std;

class extraResource
{
private:
    map<string, double> wikiMap;
    map<string, double> unigramMap;
    map<string, double> twogramMap;
    map<string, double> threegramMap;
    map<string, double> fourgramMap;
    map<string, double> fivegramMap;
public:
    extraResource(string datapath);
    ~extraResource(void);
    void loadMSGram(string datapath, string timeStr);
    void loadAll(string datapath);
    double getMsProb(string str, int wordNum);
    double getWikiProb(string str);
    int getWikiGramNum();
    map<string, double> getWikiMap();
    map<string, double> getGramMap(int gramLen);
};

