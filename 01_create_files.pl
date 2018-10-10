#!/usr/bin/env perl

###########################################################################
#                                                                         #
# Program     01_create_files.pl                                          #
# Author      Oleksandr Osavchuk                                          #
# Description                                                             #
#             Detect local mounted disk (make sure it is local)           #
#             with at least X MB free space, create Z files of size Y,    #
#             run Z “dd” processes which where each process will fill the #
#             selected file with Data and print time took to complete     #
#             the work.                                                   #
#                                                                         #
#                                                                         #
###########################################################################

use strict;
use warnings;
use POSIX qw/strftime/;

my %OS_CALL = (
                 DD         => '/bin/dd',
                 DF         => '/bin/df -lk'
               );

my $MIN_FREE_SPACE_MB    = 1;
my $CREATE_Z_FILES       = 3;
my $FILE_SIZE_BYTE       = 1024;

my $gDebug = 1;

######################################################################
#
#  Log
#
sub Log {
    my $str = shift;
    print STDOUT "$str\n";

    return 0;
}

#####################################################################
#
# check_free_space_on_local_device
#
sub check_free_space_on_local_device {
    #my $df_command = ;
    my @out = `$OS_CALL{DF}`;
    my ($device,$total,$used,$avail,$mount);
    foreach my $line ( @out ) {
        next if ( $line =~ /^Filesystem.*/i );
        ($device,$total,$used,$avail,undef,$mount) = split(' ',$line);
        Log ("[DEBUG] Splitted line: $device:$total:$used:$avail:$mount") if $gDebug;
        my $size_in_mb = $avail/1024; # calc size in MB
        # return mount point if there is enough space
        if ( $size_in_mb >= $MIN_FREE_SPACE_MB ) {
            Log ("[DEBUG] Found mount point: $mount") if $gDebug;
            return $mount;
        }
    }
    die "[ERROR] Not found local device with at least ${MIN_FREE_SPACE_MB}Mb!";
}

#####################################################################
# 
# create_files
#
sub create_files {
    my $mount_point = check_free_space_on_local_device;
    my $cmd = "find $mount_point -type d -user $ENV{USER} 2>/dev/null | head -1";
    chomp( my $folder_to_create_files = `$cmd` );
    die "[ERROR] Not found folder for $ENV{USER} user to create files!" if ( $folder_to_create_files eq '' );
    Log ( "[DEBUG] $folder_to_create_files" ) if $gDebug;

    my @counts = ( 1..$CREATE_Z_FILES );
    foreach my $count (@counts) {
        my $file_out = "'" . $folder_to_create_files . "'/file_$count";
        Log( "[${count}/$CREATE_Z_FILES] Creating file $file_out.." );
        $cmd = "$OS_CALL{DD} if=/dev/random of=$file_out bs=1 count=$FILE_SIZE_BYTE";
        my @out = `$cmd`;
        my $errcode = $?;
        Log ( "[ERROR] failed!" ) if( $errcode != 0 );
    }

    return 0;
}

#################################################################
#            Main program                                       #
#################################################################

my $start_time = time();
my $date = strftime '%A, %d %B %Y %H:%M:%S GMT', localtime;
Log ("Starting at: $date");
create_files;

my $end_time = time() - $start_time;
Log ( "[INFO] Time spent: $end_time sec" );

