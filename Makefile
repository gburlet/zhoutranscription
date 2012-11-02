CC=g++
#CFLAGS = -Wall -fno-common -fvisibility=hidden
LDFLAGS = -Wall
#LIBS = -lboost_python-mt -lpython
LIBS = 
CFLAGS = -Wall
OBJECT_PATH = Release
OBJECTS = realtime.o transcription.o
vpath %.o $(OBJECT_PATH)

ztranscribe: $(OBJECTS)
	$(CC) $(CFLAGS) -o $@ $(OBJECTS:%.o=$(OBJECT_PATH)/%.o)

dylib: $(OBJECTS)
	$(CC) -dynamiclib $(LDFLAGS) -L/usr/local/lib $(OBJECTS:%.o=$(OBJECT_PATH)/%.o) -o /usr/local/lib/libztranscribe.dylib $(LIBS)

transcription.o: transcription.cpp transcription.h plugin.h
	$(CC) $(CFLAGS) -I/usr/local/Cellar/python/2.7.3/Frameworks/Python.framework/Versions/2.7/include/python2.7 -c transcription.cpp -o $(OBJECT_PATH)/$@

realtime.o: realtime.cpp realtime.h
	$(CC) $(CFLAGS) -c $< -o $(OBJECT_PATH)/$@

clean:
	rm -rf $(OBJECT_PATH) *.dylib

$(OBJECTS): | $(OBJECT_PATH)

$(OBJECT_PATH):
	mkdir $(OBJECT_PATH)
