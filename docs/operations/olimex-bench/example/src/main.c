#include <stdio.h>

int main(void) {
    FILE *report = fopen("/test/olimex-authoring/result.txt", "wb");
    if (!report) {
        puts("OLIMTEST FAIL opening result");
        return 1;
    }

    int written = fprintf(report, "%s\n", "Result file example");
    int closed = fclose(report);
    if (written < 0 || closed != 0) {
        puts("OLIMTEST FAIL writing result");
        return 1;
    }

    puts("OLIMTEST PASS");
    return 0;
}
