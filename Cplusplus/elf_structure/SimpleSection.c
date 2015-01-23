int printf( const char* format, ...);

int global_init_var = 84;  // global variable; initialized
int global_uninit_var;  // global varibale; not intitialized

void func1( int i )
{
    printf("%d\n", i);
}

int main(void) 
{
    static int static_var = 85; // static variable; initialized
    static int static_var2; // static variable; not initialized
    int a = 1;
    int b;

    func1( static_var + static_var2 + a + b);
    
    return a;
}
