#include "Headers.h"
#include "util.h"
#include "extraResource.h"

using namespace std;

int main()
{
    util utils;
    cout << "Program starts at " << utils.getTime() << endl;
    string datapath = "..//testTools//";
    string as = "hash#usr@testa ab@cd#sd usr@usr12 rT@test hash#sd Rt rt RT test tweet";
    cout << as << endl;
    string asNew = utils.vectorToStr(utils.tweetStrToVec(as), ' ');
    cout << asNew << endl;
    cout << "Program ends at " << utils.getTime() << endl;
    return 0;
}
