# Fix `fputs` appending an extra newline

The current AgonDev implementation is contrary to the ISO C specification for `fputs`. The public C11 committee draft N1570, §7.21.7.4 paragraph 2, specifies writing the supplied string with its terminating null character excluded. It provides no additional newline. This patch restores the specified `fputs` behavior. See [N1570 §7.21.7.4, printed page 332](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf#page=350) and [§7.21.7.9, printed page 333](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf#page=351).

The file-I/O example now writes its line separators explicitly.

The patch is available in **[bgates747/agondev, branch `codex/fputs-newline`](https://github.com/bgates747/agondev/tree/codex/fputs-newline)**. Our fork retains the host regression harness separately on **[`codex/fputs-validation`](https://github.com/bgates747/agondev/tree/codex/fputs-validation)**, excluded from this PR's changes. Both branches contain identical patched library source. The test entry point is **[`tests/fputs/test-host.sh`](https://github.com/bgates747/agondev/blob/codex/fputs-validation/tests/fputs/test-host.sh)**. Expected output:

```text
fputs host tests passed
```
Prepared by Codex on behalf of Brandon
