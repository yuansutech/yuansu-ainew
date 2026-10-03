#!/usr/bin/perl
use strict;
use warnings;
use feature 'say';
my %stats = (
    total_lines => 0,
    error_count => 0,
    warn_count  => 0,
    levels      => {},
);
sub parse_line {
    my ($line) = @_;
    chomp $line;
    return undef if $line =~ /^\s*$/;
    if ($line =~ /^\[(\w+)\]\s+(.+)$/) {
        my ($level, $message) = ($1, $2);
        return { level => $level, message => $message };
    }
    return undef;
}
sub process_line {
    my ($entry) = @_;
    $stats{total_lines}++;
    $stats{levels}{$entry->{level}}++;
    if ($entry->{level} eq 'ERROR') {
        $stats{error_count}++;
    } elsif ($entry->{level} eq 'WARN') {
        $stats{warn_count}++;
    }
}
sub read_log {
    my ($filename) = @_;
    my @entries;
    open(my $fh, '<', $filename) or die "Cannot open $filename: $!";
    while (my $line = <$fh>) {
        my $entry = parse_line($line);
        next unless defined $entry;
        push @entries, $entry;
    }
    close($fh);
    return @entries;
}
sub summarize {
    my ($entries) = @_;
    for my $entry (@$entries) {
        process_line($entry);
    }
    say "Total lines: $stats{total_lines}";
    say "Errors: $stats{error_count}";
    say "Warnings: $stats{warn_count}";
    for my $level (sort keys %{$stats{levels}}) {
        say "  $level: $stats{levels}{$level}";
    }
}
my $log_data = <<'END_LOG';
[INFO] Service started
[WARN] Config missing, using defaults
[ERROR] Database connection failed
[INFO] Retrying connection
[ERROR] Retry limit exceeded
END_LOG
open(my $tmp, '>', '/tmp/test.log') or die $!;
print $tmp $log_data;
close($tmp);
my @entries = read_log('/tmp/test.log');
summarize(\@entries);
my $missing = parse_line('');
say "Missing level: " . $missing->{level};
my $unknown = $stats{levels}{'DEBUG'};
say "Debug count: $unknown";
my @sorted = sort { $a->{level} cmp $b->{level} } @entries;
say "First sorted: " . $sorted[0]{message};
unlink '/tmp/test.log';
