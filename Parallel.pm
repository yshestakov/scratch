###########################################################################
#                                                                         #
# Program     Parallel.pm                                                 #
# Author      Oleksandr Osavchuk                                          #
# Description                                                             #
#             Parallel run functions                                      #
#                                                                         #
#                                                                         #
###########################################################################

package Parallel;
use strict;
use warnings;

use POSIX ':sys_wait_h';
use POSIX qw/strftime/;
use Carp;
use English qw( -no_match_vars );

my $NUMBER_NEGATIVE_1 = -1;
my $NUMBER_0          = 0;
my $COUNT_1           = 1; # default count = 1
my $SLEEP_3           = 3;
my $MIN_60            = 60;

my %OS_CALL = (
                 PS         => '/bin/ps'
               );

# constructor
sub new {
    my $class     = shift;
    my $proc      = shift;
    my $count     = shift;
    my $timeout   = shift;

    my $self  = {
        PROC      => undef,
        COUNT     => undef,
        TIMEOUT   => undef,
        DEBUG     => undef,
        RC        => 0,
    };

    if ( not defined $proc ) { carp "[ERROR] Proc to run is not defined!"; }
    $self->{PROC}    = $proc;
    $self->{COUNT}   = ( $count   ) ? $count : $COUNT_1;
    $self->{TIMEOUT} = ( $timeout ) ? $timeout : $MIN_60 * $MIN_60; # 1 hour

    $self->{CHILDREN} = {};
    $self->{CHILDS_ERROR} = {};

    bless( $self, $class );
    return $self;
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
# parallel_run
# Return: 0 - ok
#         1 - error
#
sub parallel_run {
    my $self = shift;
    my $debug = $self->{DEBUG};
    my $date;
    my $children;
    my $childs_error;

    local $SIG{CHLD} = sub {
        my $children;
        my $childs_error;
        $children = $self->{CHILDREN};
        $childs_error = $self->{CHILDS_ERROR};

        # don't change $! and $? outside handler
        local ($ERRNO, $CHILD_ERROR) = ($ERRNO, $CHILD_ERROR);
        my $child_pid = waitpid $NUMBER_NEGATIVE_1, WNOHANG;
        if ( $child_pid == $NUMBER_NEGATIVE_1 or $child_pid == $NUMBER_0 ) { return; }
        $date = strftime '%A, %d %B %Y %H:%M:%S GMT', localtime;
        Log( "[$date] Parent: child $child_pid was reaped" );
        if ( ! defined $childs_error->{$child_pid} ) { return; }
        $childs_error->{$child_pid} = $CHILD_ERROR;
        if ( $debug ) { Log( "[DEBUG] SIG child $child_pid, rc=$CHILD_ERROR" ); }
        if ( defined $children->{$child_pid} ) { delete $children->{$child_pid}; }
        if ( $childs_error->{$child_pid} > 0 ) {
            $self->{RC} = 1;
            if ( $debug ) { Log( "[DEBUG] SIG child error for $child_pid, rc=$CHILD_ERROR" ); }
        }
    };

    eval {
        local $SIG{ALRM} = sub { $self->{RC} = 1; croak 'alarm timeout'; };
        alarm $self->{TIMEOUT};
        $self->parallel_start();
        alarm 0;
    };

    Log ( "[INFO] parallel run finished at " . ( strftime '%A, %d %B %Y %H:%M:%S GMT', localtime ) );
    if ( $EVAL_ERROR && $EVAL_ERROR !~ quotemeta 'alarm timeout' ) {
        $self->{RC} = 1; croak "[ERROR] $EVAL_ERROR";
    } else {
        foreach my $child_pid ( sort keys %$childs_error ) {
            if ( $childs_error->{$child_pid} > 0 ) {
                if ( $debug ) { Log( "[DEBUG] Child error for $child_pid, rc=" . $childs_error->{$child_pid} ); }
                $self->{RC} = 1;
                last;
            }
        }
    }

    return $self->{RC};
}

######################################################################
# parallel_start
#
sub parallel_start {
    my $self = shift;
    my $num = $self->{COUNT};
    my @counts = ( $COUNT_1..$num );
    my $start_time = time();
    my $end_time;
    my $tout;
    my $date;
    my $children;
    my $childs_error;

    $children = $self->{CHILDREN};
    $childs_error = $self->{CHILDS_ERROR};

    foreach my $count (@counts) {
        Log( "[${count}/$num] Process starting.." );
        my $child_pid = fork;
        if ( ! defined $child_pid ) { croak "[ERROR] Cannot fork: $ERRNO" };

        if ( $child_pid == 0 ) { # child
            $self->{PROC}( $count );
        } else { # parent
            $children->{$child_pid}     = $NUMBER_NEGATIVE_1;
            $childs_error->{$child_pid} = $NUMBER_NEGATIVE_1;
            $date = strftime '%A, %d %B %Y %H:%M:%S GMT', localtime;
            Log( "[INFO] [$date] child started, proc=${count},pid=$child_pid");
        }
    }

    while ( $self->parallel_children_number() ) {
        foreach my $child_pid ( sort keys %$childs_error ) {
            sleep $SLEEP_3;
            $end_time = time();
            $tout = $end_time - $start_time;
            if ( $tout >= $self->{TIMEOUT} and defined $childs_error->{$child_pid} and $childs_error->{$child_pid} == $NUMBER_NEGATIVE_1 ) {
                $date = strftime '%A, %d %B %Y %H:%M:%S GMT', localtime;
                Log( "[INFO] [$date] kill ILL $child_pid" );
                $childs_error->{$child_pid} = 1;
                kill ILL => $child_pid;
                if ( defined $children->{$child_pid} ) { delete $children->{$child_pid}; }
                waitpid $child_pid, 0;
            }
        }
    }

    return 0;

}

######################################################################
# parallel_children_number
#   return number of running childs
#
sub parallel_children_number {
    my $self = shift;
    my $children = $self->{CHILDREN};
    # check child pid from ps
    foreach my $child_pid ( sort keys %$children ) {
        my $ps_pid = `$OS_CALL{PS} -p $child_pid -o pid --no-headers`;
        if ( ! $child_pid eq $ps_pid ) { delete $children->{$child_pid}; }
    }
    if ( $self->{DEBUG} ) { Log( "[DEBUG] number of running childs: " . scalar keys %$children ); }
    return scalar keys %$children;
}

1;

__END__
