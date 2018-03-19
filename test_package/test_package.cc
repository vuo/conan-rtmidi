#include <stdio.h>
#include <RtMidi/RtMidi.h>

int main()
{
	RtMidiOut *midiout = new RtMidiOut();
	if (!midiout)
	{
		fprintf(stderr, "Error initializing RtMidi\n");
		return -1;
	}

	printf("Successfully initialized RtMidi\n");

	return 0;
}
