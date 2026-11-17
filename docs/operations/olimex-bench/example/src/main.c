#include <stdio.h>

int main(void) {
    FILE *report = fopen("/test/olimex-authoring/result.txt", "wb");
    if (!report) {
        puts("OLIMTEST FAIL opening result");
        return 1;
    }

    int written = fputs("Result file example\n", report);
    int closed = fclose(report);
    if (written == EOF || closed != 0) {
        puts("OLIMTEST FAIL writing result");
        return 1;
    }

    puts("OLIMTEST PASS");
    return 0;
}
