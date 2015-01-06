#include "jni.h"
#include "SimpleClass.h"

class SimpleClass
{
	private:
	int val;

	public:

	void setIntVal(int v) {
		val = v;
	}

	int getIntVal() {
			return val;
	}

};


JNIEXPORT jlong JNICALL Java_SimpleClass_initNativeSimpleClass
(JNIEnv * env, jobject obj) {
	//create an object
	SimpleClass* sc = new SimpleClass();

	// return the pointer to this class
	jlong pointer = reinterpret_cast<jlong>(sc);

	return pointer;
}


JNIEXPORT jint JNICALL Java_SimpleClass_getIntVal(JNIEnv * env, jobject object, jlong pointer) {
	SimpleClass* sc = reinterpret_cast<SimpleClass *>(pointer);
	return sc->getIntVal();
}

JNIEXPORT void JNICALL Java_SimpleClass_setIntVal
  (JNIEnv * env, jobject object , jlong pointer, jint value){
	SimpleClass* sc = reinterpret_cast<SimpleClass *>(pointer);
	sc->setIntVal(value);
}

JNIEXPORT void JNICALL Java_SimpleClass_destroyNativeSimpleClass
  (JNIEnv * env, jobject object, jlong pointer){
	SimpleClass* sc = reinterpret_cast<SimpleClass *>(pointer);
	// revoke memory
	delete sc;
}
