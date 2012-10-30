CC=g++
#CFLAGS = -Wall -fno-common -fvisibility=hidden
LDFLAGS = -Wall
CFLAGS = -Wall
OBJECT_PATH = Release
OBJECTS = realtime.o transcription.o
vpath %.o $(OBJECT_PATH)

ztranscribe: $(OBJECTS)
	$(CC) $(CFLAGS) -o $@ $(OBJECTS:%.o=$(OBJECT_PATH)/%.o)

dylib: $(OBJECTS)
	$(CC) -dynamiclib $(LDFLAGS) $(OBJECTS:%.o=$(OBJECT_PATH)/%.o) -o /usr/local/lib/libztranscribe.dylib

transcription.o: transcription.cpp transcription.h plugin.h
	$(CC) -c $(CFLAGS) transcription.cpp -o $(OBJECT_PATH)/$@

realtime.o: realtime.cpp realtime.h
	$(CC) -c $(CFLAGS) $< -o $(OBJECT_PATH)/$@

clean:
	rm -rf $(OBJECT_PATH) *.dylib

$(OBJECTS): | $(OBJECT_PATH)

$(OBJECT_PATH):
	mkdir $(OBJECT_PATH)
