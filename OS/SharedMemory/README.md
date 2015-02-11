进程间通信———共享内存
========
###信号量

***reference http://www.cnblogs.com/biyeymyhjob/archive/2012/07/21/2602015.html***

信号量用来协调不同进程间的数据对象，主要的应用是共享内存方式的进程间通信。
本质上，信号量是一个计数器，用来记录对某个资源（共享内存）的存取状况。
为了获得共享资源，进程需要执行下列操作：

（1） 测试控制该资源的信号量。 

（2） 若此信号量的值为正，则允许进行使用该资源。进程将信号量减1。 

（3） 若此信号量为0，则该资源目前不可用，进程进入睡眠状态，直至信号量值大于0，进程被唤醒，转入步骤（1）。 

（4） 当进程不再使用一个信号量控制的资源时，信号量值加1。如果此时有进程正在睡眠等待此信号量，则唤醒此进程。 	　　 


By using JNI (Java Native Interface), you could easily new and reference a Java object in C++ code. However, you can not new a C++ object in Java Code or return a C++ object to java. What you can do is returning the address of the C++ object [1]. This project aims to enable referencing a C++ Object in Java Code. It is inspired by this link[2] and using JNI.

In the Java layer, our code is shown below. This SimpleClass in Java is a wrapper class for SimpleClass in C++. We keep the nativePtr stores the C++ object address. This C++ object is created in C++ layer and its address is returned to Java layer. So when we want to get the value of this object's int member, we need to pass this address to C++ layer. So we define` private native int getIntVal(long ptr);`. Moreover, `private native void destroyNativeSimpleClass(long nativePtr);` is responsible to delete the C++ object in C++ layer.

	public class SimpleClass {
	    public long nativePtr = 0L;

	    public SimpleClass() {
	        nativePtr = initNativeSimpleClass();
	    }

	    public void destroy() {
	        destroyNativeSimpleClass(nativePtr);
	        nativePtr = 0L;
	    }

	    protected void finalize() throws Throwable {
	    	if (nativePtr != 0L){
	    		destroyNativeSimpleClass(nativePtr);
	    		nativePtr = 0L;
	    	}
	    }

	    public int getIntVal(){
	    	return getIntVal(nativePtr);
	    }
	    
	    public void setIntVal(int val) {
	    	setIntVal(nativePtr, val);
	    }
	    
	    /* native functions which should be implemented in C++ layer*/
	    private native int getIntVal(long ptr);
	    private native void setIntVal(long ptr, int val);

	    private native long initNativeSimpleClass();
	    private native void destroyNativeSimpleClass(long nativePtr);

	}


Our test code like that:
	
	public class TestSimpleClass {

	    public static void main(String[] args) throws IOException{
	    	System.loadLibrary("simpleclass"); 
	    	
	    	//create the C++ object
	    	SimpleClass sc = new SimpleClass();
	    	System.out.println("The address: " + sc.nativePtr);
	    	
	    	sc.setIntVal(250);
	    	System.out.println(sc.getIntVal());
	    
	    	sc.setIntVal( 200);
	    	System.out.println(sc.getIntVal());
	    	
	    	//destory the object
	    	sc.destroy();
	    	System.out.println("The address: " + sc.nativePtr);
	    
	    }
	}



You can do following steps to run this project:

	cd call-cpp-object-demo
	javac *.java -d bin
	cd bin
	javah -d ../jni -jni SimpleClass
	cd ../jni
	make
	cd ../bin
	java -Djava.library.path=../lib TestSimpleClass
	
You will see the result like this:

	The address: 140589752997808
	250
	200
	The address: 0

It is clear that after writing the Java wrapper for C++, we can operate upon a C++ object in Java code. 


###Reference
[1] http://stackoverflow.com/questions/3095497/jni-and-using-c-newed-objects-in-java

[2] http://stackoverflow.com/questions/10212851/can-i-reference-c-objects-in-java-code-using-jni	
	
	

