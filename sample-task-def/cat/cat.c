#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#define BUFFER_SIZE 255


char *concat4( const char *s1, const char *s2, const char *s3, const char* s4 )
{
    size_t l1, l2, l3, l4;
    char *r;

    l1 = l2 = l3 = l4 = 0;

    if( s1 )
        l1 = strlen( s1 );

    if( s2 )
        l2 = strlen( s2 );

    if( s3 )
        l3 = strlen( s3 );

    if( s4 )
        l4 = strlen( s4 );

    r = malloc( sizeof(char) * (l1 + l2 + l3 + l4 + 1) );
    r[0] = '\0';

    if( s1 )
        strcpy( r, s1 );

    if( s2 )
        strcpy( r + l1, s2 );

    if( s3 )
        strcpy( r + l1 + l2, s3 );

    if( s4 )
        strcpy( r + l1 + l2 + l3, s4 );

    return r;
}


int handle_argument( const char *cmdline, const char *arg )
{
    char buffer[BUFFER_SIZE];
    ssize_t rresult, wresult, cresult, padding;
    int fd, doclose;
    char *msg;

    if( !strcmp( arg, "-" ) )
    {
        doclose = 0;
        fd = STDIN_FILENO;
    }
    else
    {
        doclose = 1;
        fd = open( arg, O_RDONLY );
        if( fd < 0 )
        {
            msg = concat4( cmdline, ": cannot open '", arg, "' for reading" );
            perror( msg );
            free( msg );
            return 1;
        }
    }

    while( ( rresult = read( fd, buffer, BUFFER_SIZE ) ) > 0 )
    {
        padding = 0;
        while( padding < rresult )
        {
            wresult = write( STDOUT_FILENO,
                             buffer + padding,
                             rresult - padding );
            padding += wresult;
        }
    }

    if( doclose )
    {
        cresult = close( fd );
    }

    return 0;
}


int main( int argc, char **argv ) {
    int i, result = 0;
    if( argc == 1 )
        result |= handle_argument( argv[0], "-" );
    else
    {
        for( i = 1; i < argc; ++i )
            result |= handle_argument( argv[0], argv[i] );
    }

    return result;
}
