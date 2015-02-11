使用 Java Native Interface 的最佳实践
========
Notes for http://www.ibm.com/developerworks/cn/java/j-jni/

##性能缺陷
### 1. 查找并全局缓存常用的类、字段 ID 和方法 ID。
距离来说使用JNI调用静态方法，方法，获取字段，需要JVM完成大量的工作，所以应该缓存这些操作。


	int sumValues2(JNIEnv* env, jobject obj, jobject allValues){
	   jclass cls = (*env)->GetObjectClass(env,allValues);
	   jfieldID a = (*env)->GetFieldID(env, cls, "a", "I");
	   jfieldID b = (*env)->GetFieldID(env, cls, "b", "I");
	   jfieldID c = (*env)->GetFieldID(env, cls, "c", "I");
	   jfieldID d = (*env)->GetFieldID(env, cls, "d", "I");
	   jfieldID e = (*env)->GetFieldID(env, cls, "e", "I");
	   jfieldID f = (*env)->GetFieldID(env, cls, "f", "I");
	   jint avalue = (*env)->GetIntField(env, allValues, a);
	   jint bvalue = (*env)->GetIntField(env, allValues, b);
	   jint cvalue = (*env)->GetIntField(env, allValues, c);
	   jint dvalue = (*env)->GetIntField(env, allValues, d);
	   jint evalue = (*env)->GetIntField(env, allValues, e);
	   jint fvalue = (*env)->GetIntField(env, allValues, f);
	   return avalue + bvalue + cvalue + dvalue + evalue + fvalue
	}

每次调用该方法时都需要用 3,572 ms 运行了 10,000,000 次。清单 3 用了 86,217 ms — 多花了 24 倍的时间。调用JVM六次，不如将这些字段id缓存起来。


#####HOW TO REALIZE IT?

Follow this code from [3].

	jmethodID limitMethodId;
	jfieldID limitFieldId;

	// Is automatically called once the native code is loaded via System.loadLibary(...);
	jint JNI_OnLoad(JavaVM* vm, void* reserved) {
	    JNIEnv* env;
	    if ((*vm)->GetEnv(vm, (void **) &env, JNI_VERSION_1_6) != JNI_OK) {
	        return JNI_ERR;
	    } else {
	        jclass cls = (*env)->FindClass("java/nio/Buffer");
	        // Get the id of the Buffer.limit() method.
	        limitMethodId = (*env)->GetMethodID(env, cls, "limit", "()I");

	        // Get int limit field of Buffer
	        limitFieldId = (*env)->GetFieldID(env, cls, "limit", "I");
	    }
	}
	
	
### 2. 获取和更新仅本机代码需要的数组部分。在只要数组的一部分时通过适当的 API 调用来避免复制整个数组。

如果您对含有 1,000 个元素的数组调用 GetLongArrayElements()，则会造成至少分配或复制 8,000 字节的数据（每个 long 1,000 元素 * 8 字节）。当您随后使用 ReleaseLongArrayElements() 更新数组的内容时，需要另外复制 8,000 字节的数据来更新数组。即使您使用较新的 GetPrimitiveArrayCritical()，规范仍然准许 ***JVM 创建完整数组的副本***。

GetTypeArrayRegion() 和 SetTypeArrayRegion() 方法允许您获取和更新数组的一部分，而不是整个数组。通过使用这些方法访问较大的数组，您可以确保***只复制本机代码将要实际使用的数组部分***。

	jlong getElement(JNIEnv* env, jobject obj, jlongArray arr_j, 
	                 int element){
	   jboolean isCopy;
	   jlong result;
	   jlong* buffer_j = (*env)->GetLongArrayElements(env, arr_j, &isCopy);
	   result = buffer_j[element];
	   (*env)->ReleaseLongArrayElements(env, arr_j, buffer_j, 0);
	   return result;
	}
 

	jlong getElement2(JNIEnv* env, jobject obj, jlongArray arr_j, 
	                  int element){
	     jlong result;
	     (*env)->GetLongArrayRegion(env, arr_j, element,1, &result);
	     return result;
	}

### 3. 在单个 API 调用中尽可能多地获取或更新数组内容。如果可以一次较多地获取和更新数组内容，则不要逐个迭代数组中的元素。
### 4. 如果可能，将各参数传递给 JNI 本机代码，以便本机代码回调 JVM 获取所需的数据。
在调用某个方法时，您经常会在传递一个有多个字段的对象以及单独传递字段之间做出选择。
传递对象？or 传递单个字段？

在面向对象设计中，传递对象通常能提供较好的封装，因为对象字段的变化不需要改变方法签名。但是，对于 JNI 来说，本机代码必须通过一个或多个 JNI 调用返回到 JVM 以获取需要的各个字段的值。这些额外的调用会带来额外的开销，因为从本机代码过渡到 Java 代码要比普通方法调用开销更大。因此，对于 JNI 来说，本机代码从传递进来的对象中访问大量单独字段时会导致性能降低。

下面的程序中，每次访问对象的一个字段都需要call JVM，让JVM帮我们取出来字段值，所以如果使用JNI的话还是不要传对象了~


	int sumValues(JNIEnv* env, jobject obj, jint a, jint b,jint c, jint d, jint e, jint f){
	   return a + b + c + d + e + f;
	}

	int sumValues2(JNIEnv* env, jobject obj, jobject allValues){

	   jint avalue = (*env)->GetIntField(env, allValues, a);
	   jint bvalue = (*env)->GetIntField(env, allValues, b);
	   jint cvalue = (*env)->GetIntField(env, allValues, c);
	   jint dvalue = (*env)->GetIntField(env, allValues, d);
	   jint evalue = (*env)->GetIntField(env, allValues, e);
	   jint fvalue = (*env)->GetIntField(env, allValues, f);
	   
	   return avalue + bvalue + cvalue + dvalue + evalue + fvalue;
	}

sumValues2() 方法需要 6 个 JNI 回调，并且运行 10,000,000 次需要 3,572 ms。其速度比 sumValues() 慢 6 倍，前者只需要 596 ms。通过传递 JNI 方法所需的数据，sumValues() 避免了大量的 JNI 开销。

### 5. 定义 Java 代码与本机代码之间的界限，最大限度地减少两者之间的互相调用。

### 6. 构造应用程序的数据，使它位于界限的正确的侧，并且可以由使用它的代码访问，而不需要大量跨界调用。

### 7. 当本机代码造成创建大量本地引用时，在各引用不再需要时删除它们。

	void workOnArray(JNIEnv* env, jobject obj, jarray array){
	   jint i;
	   jint count = (*env)->GetArrayLength(env, array);
	   for (i=0; i < count; i++) {
	      jobject element = (*env)->GetObjectArrayElement(env, array, i);
	      if((*env)->ExceptionOccurred(env)) {
	         break;
	      }
	      
	      /* do something with array element */
	   }
	}

每次调用GetObjectArrayElement()时都会为元素创建一个本地引用，并且知道本机代码运行完成时才会释放。数组越大，所创建的本地引用就越多。

所以应该使用JNI `DeleteLocalRef()`来删除本地引用。

	void workOnArray(JNIEnv* env, jobject obj, jarray array){
	   jint i;
	   jint count = (*env)->GetArrayLength(env, array);
	   for (i=0; i < count; i++) {
	      jobject element = (*env)->GetObjectArrayElement(env, array, i);
	      if((*env)->ExceptionOccurred(env)) {
	         break;
	      }
	      
	      /* do something with array element */

	      (*env)->DeleteLocalRef(env, element);
	   }
	}

### 8. 如果某本机代码将同时存在大量本地引用，则调用 JNI EnsureLocalCapacity() 方法通知 JVM 并允许它优化对本地引用的处理。

##正确性缺陷
### 1. 仅在相关的单一线程中使用 JNIEnv。
JNI规范规定每个JNIEnv对于线程来说都是本地的。JVM可以依赖于这一假设，将额外的线程本地信息存储在JNIEnv中。一个线程使用另一个线程的JNIEnv会导致难以调试的小问题。

### 2. 在发起可能会导致异常的 JNI 调用后始终检测异常。
	jclass objectClass;
	jfieldID fieldID;
	jchar result = 0;

	objectClass = (*env)->GetObjectClass(env, obj);
	fieldID = (*env)->GetFieldID(env, objectClass, "charField", "C");
	if((*env)->ExceptionOccurred(env)) {
	   return;
	}
	result = (*env)->GetCharField(env, obj, fieldID);

考虑调用GetFieldID()的代码，如果无法找到所请求的字段，则会出现NoSuchFieldError。如果本机代码继续运行而未检测异常，并使用该字段ID，则会造成程序崩溃。

### 4. 不要忘记为每个 GetXXX() 使用模式 0（复制回去并释放内存）调用 ReleaseXXX()。
即便使用Critical版本，也无法保证您能获得对数组或字符串的直接饮用。一些JVM始终返回一个副本，并且在这些JVM中，如果您在 ReleaseXXX() 调用中指定了 JNI_ABORT，或者忘记调用了 ReleaseXXX()，则对数组的更改不会被复制回去。

	void modifyArrayWithRelease(JNIEnv* env, jobject obj, jarray arr1) {
	   jboolean isCopy;
	   jbyte* buffer = (*env)-> (*env)->GetByteArrayElements(env,arr1,&isCopy);
	   if ((*env)->ExceptionCheck(env)) return; 
	   
	   buffer[0] = 1;

	   (*env)->ReleaseByteArrayElements(env, arr1, buffer, JNI_COMMIT);
	   if ((*env)->ExceptionCheck(env)) return;
	}

### 5. 确保代码不会在 GetXXXCritical() 和 ReleaseXXXCritical() 调用之间发起任何 JNI 调用或由于任何原因出现阻塞。

MY OPINION： 还是尽量别用Criticall版本函数了，反正他也没法保证获取对数组或者字符串的直接引用，规范仍然允许JVM创建副本。其实JVM总是不给你direct pointer，他`always compy`[2]。


What about ByteBuffer?
Newer Java releases have java.nio, and that gives you ByteBuffer for explicitly sharing a byte buffer between Java and JNI code. This potentially lets you avoid all the copying, but it's not necessarily convenient if you're trying to fit in with an older API. If you're implementing a new kind of InputStream or OutputStream, for example, this isn't really an option. But if you could use a ByteBuffer, it may be your best choice. [2]

###Referenc
[1] http://www.ibm.com/developerworks/cn/java/j-jni/

[2] http://elliotth.blogspot.com/2007/03/optimizing-jni-array-access.html
	
[3] http://normanmaurer.me/blog/2014/01/07/JNI-Performance-Welcome-to-the-dark-side/

