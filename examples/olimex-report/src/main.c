#include <stdio.h>

#include "report_writer.h"

int main(int argc, char **argv)
{
    static const char result[] = "Report lifecycle example\n";
    if (argc != 2 || !olx_report_token(argv[1])) {
        puts("OLXREPORT FAIL: invalid attempt argument");
        return 1;
    }

    /* Run the fixture's workload here. Save only after timing has ended. */
    if (olx_report_save(argv[1], "/test/extender/report-example/direct/REPORT.TXT",
                        result, sizeof(result) - 1)) {
        puts("OLXREPORT FAIL: report I/O");
        return 1;
    }
    puts("OLXREPORT PASS");
    return 0;
}
