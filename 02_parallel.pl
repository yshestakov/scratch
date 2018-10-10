#!/usr/bin/env perl

###########################################################################
#                                                                         #
# Program     02_parallel.pl                                              #
# Author      Oleksandr Osavchuk                                          #
# Description                                                             #
#             Run user-selected command on many servers (user provided as #
#             param) with ssh in parallel, collect output from all nodes. #
#             Script should print collected output from all nodes on      #
#             stdout, w/o using temp files.                               #
#                                                                         #
#                                                                         #
###########################################################################

use strict;
use warnings;
use POSIX qw/strftime/;
use Getopt::Std;
use File::Basename;
use English qw( -no_match_vars );
use Parallel;

my $USER_COMMAND = '/bin/ps';

my $gDebug = 1;
my $me = basename( $PROGRAM_NAME );
my @servers;

######################################################################
sub usage {

    Log( 'Usage:' );
    Log( " $me [SERVERS] " );
    Log( ' Optional arguments:' );
    Log( '          -d debug' );

    exit 1;
}

######################################################################
#
#  Log
#
sub Log {
    my $str = shift;
    print STDOUT "$str\n";

    return 0;
}

######################################################################
#
#  process_args
#
sub process_args {
    my %opts;

    if ( !getopts( 'hd', \%opts ) ) {
        usage();
    }

    if ( defined $opts{'h'} ) {
        usage();
    }

    if ( defined $opts{'d'} ) {
        $gDebug = 1;
    }

    if ( @ARGV < 1 ) { usage(); }
    @servers = @ARGV;

    return 0;
}

######################################################################
# run_ssh_child
#
sub run_ssh_child {
    my $count = shift;
    my $host = ${servers}[$count-1];
    my $cmd = "ssh $host \"$USER_COMMAND\"";
    Log ("[INFO] command: $cmd");
    my @out = `$cmd`;
    my $errcode = $?;
    my $trace_out = "\n";
    # show the output
    foreach my $line ( @out ) {
        $trace_out .= $line;
    }
    Log ( $trace_out );
    Log ( "[ERROR] failed!" ) if( $errcode != 0 );

    exit $errcode;
}

######################################################################
# run_ssh
#
sub run_ssh {
    my $proc = Parallel->new( sub { run_ssh_child(@_); }, scalar @servers);
    $proc->{DEBUG} = $gDebug;
    my $rc = $proc->parallel_run();
    return $rc;
}

#################################################################
#            Main program                                       #
#################################################################

my $date = strftime '%A, %d %B %Y %H:%M:%S GMT', localtime;
Log ("Starting at: $date");
process_args;
run_ssh;

