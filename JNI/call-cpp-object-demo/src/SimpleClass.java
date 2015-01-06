// inspired from 
// http://stackoverflow.com/questions/10212851/can-i-reference-c-objects-in-java-code-using-jni

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
