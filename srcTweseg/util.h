#pragma once
#include "Headers.h"

using namespace std;

typedef pair<vector<string>, double> PAIR;

class util
{
public:
    util(void);
    ~util(void);

// vector <-> string
    string vectorToStr(vector<string> vec, char delimiter);
    string vecToStr(vector<string> vec, char delimiter, int begin, int end);
    vector<string> strToVector(string str);
    vector<string> tweetStrToVec(string str);

// string related functions
    string trimStr(string source);
    string toLower(string source);

// system related functions
    string getTime();

// math functions
    double sigmoid(double x);
};

