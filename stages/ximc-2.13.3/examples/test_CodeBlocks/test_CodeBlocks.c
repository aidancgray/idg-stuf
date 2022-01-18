#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include <ximc.h>

int main (int argc, char* argv[])
{
//	device_t is the type provided by the libximc library.
	device_t device;
	char ximc_version_str[32];
	const int seconds = 3;

	if (argc != 2) {
		printf("Usage: %s device \n", argv[0]);
		printf("Example: %s xi-com:\\\\.\\COM42 \n", argv[0]);
		printf("Example: %s xi-emu:///C:\\file.bin \n", argv[0]);
		printf("Example: %s xi-net://192.168.0.1/23456789 \n", argv[0]);
		return(1);
	}

	printf( "This is a ximc test program.\n" );
//	ximc_version returns library version string.
	ximc_version( ximc_version_str );
	printf( "libximc version %s\n", ximc_version_str );

//  Sets bindy (network) keyfile. Must be called before any call to "enumerate_devices" or "open_device" if you
//  wish to use network-attached controllers. Accepts both absolute and relative paths, relative paths are resolved
//  relative to the process working directory. If you do not need network devices then "set_bindy_key" is optional.
	set_bindy_key("keyfile.sqlite");

	printf( "Opening device...");
//	Open device by device name
	device = open_device( argv[1] );
	if (device == device_undefined) {
		printf("failed.\n");
		return(2);
	}
	printf( "done.\n" );

	printf( "Rotating to the left for %d seconds...", seconds);
	command_left( device );
	msec_sleep( seconds*1000 );
	printf( "\n" );

	printf( "Stopping engine..." );
	command_stop( device );
	printf( "done.\n" );

	printf( "Closing device..." );
	close_device( &device );
	printf( "done.\n" );

	return 0;
}
