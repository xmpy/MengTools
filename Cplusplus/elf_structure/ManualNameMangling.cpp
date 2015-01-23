
// g++ ManualNameManling.cpp -o ManualNameMangling

# include <stdio.h>

namespace myname {
    int var = 43;
}

extern "C" double _ZN6myname3varE;

int main()
{
    printf("%d\n", _ZN6myname3varE);
    return 0;
}


