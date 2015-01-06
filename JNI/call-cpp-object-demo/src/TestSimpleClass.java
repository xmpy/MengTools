import java.io.IOException;


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
