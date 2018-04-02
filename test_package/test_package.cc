#include <stdio.h>
#include <RtMidi/RtMidi.h>

int main()
{
	try
	{
		RtMidiOut *midiout = new RtMidiOut();
		if (!midiout)
		{
			fprintf(stderr, "Error initializing RtMidi\n");
			return -1;
		}

		printf("Successfully initialized RtMidi\n");
	}
	catch (RtError &e)
	{
		if (e.getType() == RtError::DRIVER_ERROR)
			printf("Couldn't open driver, but we made it this far so RtMidi itself is working.\n");
		else
			fprintf(stderr, "Error initializing RtMidi: %s\n", e.what());
	}

	return 0;
}
