//mapper
//

#include <stdio.h>
#include <string>
#include <iostream>

using namespace std;

int main() {
    string key;
    string value = "1";
    while (cin >> key) {
        cout << key << "\t" << value << endl;
    }
    return 0;
}
