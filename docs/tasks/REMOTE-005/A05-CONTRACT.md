# R05-A05 — synchronous application transfer helper

Implement the linked application caller boundary next. Reuse EMOS's resident
SD transport and the foreground checked file engine; do not load an EMOSlet over
the caller. Controlled-peer tests establish both directions before P4 staging
exists. They do not qualify WebDAV or persistent P4 spool behavior.

A05-01 [ ] Extend resident `ext.sdlink` with application-owned open, using actual
EMOS execution policy. Core/ISR/nested callers cannot acquire it. Return a fresh
execution token; retain only bounded transport buffers and ownership in ROM/RAM.
Route control replies to the application's mailbox only while this owner exists.
Existing manual listener calls and external CLI admission retain their behavior.

A05-02 [ ] Add a synchronous linked C helper for P4-to-Agon receive and
Agon-to-P4 send. Validate/copy two absolute ASCII paths, negotiate capabilities,
fragment APP_BEGIN descriptors, bind the file session to the returned job/grant,
and close ownership on every return. The caller supplies an optional cancellation
predicate; the helper does not impose Escape or retain a callback afterward.
The first supported caller ABI is AgonDev ADL C, ordinary applications/MOSlets.

A05-03 [ ] Reuse existing checked file records and mainboard file engine.
The application initiates every exchange. Receive reads a P4 source and stages/
activates the Agon destination through the existing checked engine. Send reads
the Agon source and requests P4 checked staging/activation. Do not report success
before matching terminal confirmation. No retry of an uncertain mutation. Preserve
recovery evidence on interruption; no whole-directory or fast option in this helper.

A05-04 [ ] Execute host tests with real helper/file-engine code and a controlled
peer: both directions, binary/chunk boundaries, wrong identities/CRC, unavailable
peer, busy/unsupported, cancellation before and during transfer, and caller-memory
preservation. Check the existing listener separately. Compile the ADL fixture and
EMOS through maintained wrappers; measure added ROM and stop if it will not fit.

A05-05 [ ] Exercise actual eZ80 caller execution before hardware deployment where
supported. Physical tests require a paired application-capable peer; never advertise
support through the normal P4 image before A06 supplies its staging implementation.
Record tested versus deferred boundaries and leave the bench recoverable.

## Implementation decisions and references

1. The helper owns foreground file work; EMOS owns the UART, route and application
   lease. P4 cannot assert application execution origin through an incoming packet.
2. Fresh application negotiation initially uses Legacy only. Active ExCom transport
   remains unavailable until the paired parser tranche; no implicit mode switch.
3. The app exchanges the unchanged 20-byte-header file records as a client under
   a derived session after READY. External idle service retains its own lifecycle.
4. Reuse sibling-file recovery initially, as documented in the SD layout. An
   interrupted transfer may need explicit recovery; do not delete the only good copy.
5. Official docs baseline: agon-docs `f9806bd3`, docs/mos/API.md (ADL API, public
   file calls). Stock MOS remains clean v3.0.2, `83364093`. EMOS implementation
   references: src/emos.c gateway/policy, src/emos_sdlink.c transport,
   projects/sdserve/src/service.c checked file engine. Existing source review is
   [A02](ADMISSION-REVIEW.md); numeric control contract is
   [A03](ADMISSION-CONTRACT.md). These are private Extender operations, not new
   official MOS slots or direct application UART access.

Frozen for execution under Author's instruction to proceed to the next planned
step, 2026-09-27. Existing version preapproval applies; physical bench is available.
