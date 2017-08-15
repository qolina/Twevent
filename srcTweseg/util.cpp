#ifndef util_H_
#define util_H_
#include "util.h"

util::util(void)
{
}


util::~util(void)
{
}

vector<string> util::strToVector(string str)
{
	vector<string> vec;
	istringstream iss (str);
	string w ;
	while (iss >> w) { vec.push_back(w); }
	return vec;
}
// delete all characters after @# in a word
// delete rt RT rT Rt
vector<string> util::tweetStrToVec(string str)
{
	vector<string> vec;
	istringstream iss (str);
	string w ;
    string newWord;
	while (iss >> w)
    {
//        cout << "Before: " << w;
        newWord = w;
        if(newWord.find('@') != string::npos){
            newWord.erase(newWord.find('@'));
        }
        if(newWord.empty()){
            continue;
        }
        if(newWord.find('#') != string::npos){
            newWord.erase(newWord.find('#'));
        }
        if(newWord.empty()){
            continue;
        }
        if(toLower(newWord).compare("rt") == 0){
            continue;
        }
        vec.push_back(newWord);
//        cout << " After: " << newWord << endl;
    }
	return vec;
}

string util::vectorToStr(vector<string> vec, char delimiter)
{
	string vecStr;
//    for each(string item in vec)
    for (int i = 0; i < vec.size()-1; i ++)
    {
        string item = vec[i];
        vecStr.append(item + delimiter);
    }
    vecStr.append(vec[vec.size()-1]);
    return vecStr;
}

string util::vecToStr(vector<string> vec, char delimiter, int begin, int end)
{
	string vecStr;
    for (int i = begin; i < end-1; i ++)
    {
        string item = vec[i];
        vecStr.append(item + delimiter);
    }
    vecStr.append(vec[end-1]);
    return vecStr;
}

// string functions
string util::trimStr(string source)
{
    int begin, end;
    for (int i = 0; i < source.length(); i ++)
    {
        if(source[i] != ' ')
        {
            begin = i;
            break;
        }
    }
    for (int i = source.length()-1; i >= 0; i --)
    {
        if(source[i] != ' ')
        {
            end = i;
            break;
        }
    }
    if (begin > -1 && end >= begin)
    {
        return source.substr(begin, end-begin+1);
    }
}

string util::toLower(string source)
{
    for(int i = 0; i < source.length(); i ++)
    {
        if(isupper(source[i]))
        {
            source[i] = tolower(source[i]);
        }
    }
    return source;
}

// system functions
string util::getTime()
{
    time_t timeSecs;
    struct tm * timeinfo;
    time(&timeSecs);
    timeinfo = localtime(&timeSecs);
    string timeStr = string(asctime(timeinfo));
    return timeStr.substr(0,timeStr.length()-1);
}

// math functions
double util::sigmoid(double x)
{
    return 1.0 / (1.0 + exp(-1.0 * x));
}
#endif

