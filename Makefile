CC=g++
PNAME=polytrans

polytrans: realtime.o transcription.o 
	$(CC) -o $(PNAME) transcription.o realtime.o

transcription.o: transcription.h transcription.cpp plugin.h realtime.h
	$(CC) -c transcription.cpp

realtime.o: realtime.cpp realtime.h
	$(CC) -c realtime.cpp

clean:
	rm $(PNAME) *.o
