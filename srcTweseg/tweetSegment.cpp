// tweetSegment.cpp : Defines the entry point for the console application.
//

#include "segmenter.h"
#include "Headers.h"
#include "extraResource.h"
#include "util.h"
using namespace std;

int main()
{
    util utils;
    cout << "Program starts at " << utils.getTime() << endl;
//    string datapath = "..//Data//";
    string datapath = "..//Data_hfmon//";
//    string datapath = "..//Data_Jan02//";
    string toolpath = "..//Tools//";
    string seggedpath = datapath + "segged_qtwe//";
    segmenter twesegger;
    int nullTweetNum = 0;
    extraResource resource(toolpath);
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
            string subFileName = datapath+dname;
            string outFileName = seggedpath + "segged_" + dname;
            ifstream infile(subFileName.c_str());
            ofstream outfile(outFileName.c_str());
            // load gram's msprob
            resource.loadMSGram(toolpath, timeStr);
            if(! infile)
            {
                cout << "Error openning: " << subFileName << "\n";
            }
            else
            {
                cout << "Reading file: " << subFileName << endl;
                string lineStr;
                while (getline(infile,lineStr))
                {
                    lineIndex += 1;
                    vector<string> tweet = utils.tweetStrToVec(lineStr);
//                    cout << tweet.size() << " : " << utils.vectorToStr(tweet, ' ')  << "\n";
                    string tweetIDStr = tweet.front();
                    tweet.erase(tweet.begin()); // erase tweetIDStr
                    if (tweet.size() == 0)
                    {
                        nullTweetNum += 1;
                        continue;
                    }
                    // to lower
                    tweet = utils.strToVector(utils.toLower(utils.vectorToStr(tweet,' ')));
                    // segment tweet
                    pair<vector<string>, double> seggedPair = twesegger.segment(tweet, 5, 5, resource);
                    double prob = seggedPair.second;
//                    cout << prob << "\t#" << utils.vectorToStr(seggedPair.first, '|') << endl;
                    outfile << tweetIDStr << "\t" << prob << "\t" << utils.vectorToStr(seggedPair.first, '|') << endl;
                    if (lineIndex % 10000 == 0)
                    {
                        cout << "### " << lineIndex << " tweets have been processed." << endl;
                    }
                }
                infile.close();
                outfile.close();
                cout << outFileName << " has been writen at " << utils.getTime() << endl;
            }
        }
        closedir(dirp);
    }
    cout << "All tweet number: " << lineIndex << endl;
    cout << "Null tweet number: " << nullTweetNum << endl;

    cout << "Program ends at " << utils.getTime() << endl;
    return 0;
}

