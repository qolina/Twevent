#include <stdio.h>
#include <dirent.h>
#include <stdlib.h>
#include <string>
#include <iostream>
#include <fstream>

using namespace std;
int main()
{
	string datapath = "..//Data//";
    DIR* dirp;
    struct dirent* direntp;
    dirp = opendir((char*)datapath.c_str());
    if( dirp != NULL ) {
        for(;;) {
            direntp = readdir(dirp);
            if(direntp == NULL) break;
            string dname = direntp->d_name;
            if(dname == "."){ continue; }
            if(dname == ".."){ continue; }
            char* subFileName = (char*)(datapath+dname).c_str();
			cout << "Reading file: " << subFileName << endl;
			ifstream infile(subFileName);
            char* outputFileName = "..//Data//outputfile.txt";
            //char* outputFileName = subFileName;

            ofstream outfile();
			if(! infile)
			{
				cout << "Error openning: " << subFileName << endl;
			}
			else
			{
				string lineStr;
				while (getline(infile,lineStr))
				{
                    cout << lineStr << endl;
                    outfile << lineStr[15];
                    outfile.flush();
                }

            }
            infile.close();
            outfile.close();
        }
        closedir(dirp);
    }
    return 0;
}
