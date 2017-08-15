#pragma once
#include "util.h"
#include "Headers.h"
#include "extraResource.h"

using namespace std;

class segmenter
{
private:
    map<string, double> wikiMap;
    map<string, double> unigramMap;
    map<string, double> twogramMap;
    map<string, double> threegramMap;
    map<string, double> fourgramMap;
    map<string, double> fivegramMap;
    double getMSprob(string str);
    double getWikiprob(string str);
public:
	segmenter();
	~segmenter(void);
	map <string, int> getNgram(vector<string> tweet, int u, int e);
	pair<vector<string>, double> segment(vector<string> tweet, int u, int e, extraResource& resource);
};

