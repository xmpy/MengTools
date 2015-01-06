CC=g++
FLAGS=-m64 -dynamiclib -fPIC
LIBRARY=-L/usr/local/lib
JAVA_INCLUDE=/System/Library/Frameworks/JavaVM.framework/Headers
INCLUDE=-I/usr/local/include -I$(JAVA_INCLUDE)
SRC=SimpleClass.cpp
OUT=../lib/libsimpleclass.jnilib

MAC:
	$(CC) $(FLAGS) ${LIBRARY} $(INCLUDE) $(SRC) -o $(OUT) 
