CC=g++
CFLAGS = -Wall
OBJECT_PATH = Release
OBJECTS = transcription.o realtime.o
vpath %.o $(OBJECT_PATH)

polytrans: $(OBJECTS) 
	$(CC) -o $@ $(OBJECT_PATH)/*.o

transcription.o: transcription.cpp transcription.h plugin.h realtime.h
	$(CC) -c $(CFLAGS) $< -o $(OBJECT_PATH)/$@

realtime.o: realtime.cpp realtime.h
	$(CC) -c $(CFLAGS) $< -o $(OBJECT_PATH)/$@

$(OBJECTS): | $(OBJECT_PATH)

$(OBJECT_PATH):
	mkdir $(OBJECT_PATH)

clean:
	rm -rf $(OBJECT_PATH) polytrans
