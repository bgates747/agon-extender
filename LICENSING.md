# Licensing

## Project license

Agon Extender is distributed as free software under the **GNU General Public
License, version 3 only** (`GPL-3.0-only`), except where an individual file or
third-party component carries a different compatible license notice.

Unless a file states otherwise, original code written specifically for Agon
Extender is licensed under:

```text
SPDX-License-Identifier: GPL-3.0-only
```

The root [LICENSE](LICENSE) contains the complete text of the GNU General
Public License version 3.

This document describes the project's licensing and attribution policy. It does
not replace the full text of the GPL or any third-party license notice.

---

## Why GPLv3

Agon Extender incorporates, adapts, or is expected to incorporate portions of
existing open-source projects, most importantly FabGL/vdp-gl code used by the
Agon VDP graphics stack.

FabGL source is licensed under the GNU General Public License, version 3, with
its source headers granting use under **version 3 or, at the recipient's option,
any later version**. Agon Extender chooses the version-3 option for the combined
project and distributes the combined work under `GPL-3.0-only`.

This project-level choice does **not** rewrite or narrow the license originally
offered by an upstream author. Original upstream copyright and license notices
must be preserved where required.

---

## FabGL / vdp-gl-derived material

Some Agon Extender source may contain code copied, extracted, adapted, or
mechanically derived from FabGL or its vdp-gl derivative.

Relevant upstream attribution includes:

```text
Created by Fabrizio Di Vittorio
Copyright (c) 2019-2022 Fabrizio Di Vittorio.
```

FabGL states that the library and related software are available under GPLv3,
and its source headers permit redistribution and modification under GNU GPL
version 3 or, at the recipient's option, any later version.

For FabGL/vdp-gl-derived material:

- preserve the upstream author and copyright notices;
- preserve any meaningful upstream provenance comments;
- do not describe the upstream work itself as project-original;
- do not remove an upstream license notice merely because the surrounding
  Agon Extender project is GPL-3.0-only;
- adapted or mixed-origin files should clearly identify the upstream-derived
  portions.

Where a file combines FabGL/vdp-gl-derived material with new Agon Extender
code licensed `GPL-3.0-only`, the combined file may be distributed under
GPLv3-only while retaining the original FabGL attribution and provenance.

FabGL also mentions the availability of a separate commercial license from its
author. That does not alter the GPL rights under which Agon Extender uses the
open-source code.

---

## Agon VDP-derived material

The official Agon Platform VDP is published under the **MIT License**.

If Agon Extender copies or adapts material from Agon VDP:

- retain the original MIT copyright and license notice applicable to that
  material;
- identify the upstream source where practical;
- do not replace the upstream MIT notice with a claim that the original code
  was authored as part of Agon Extender.

MIT-licensed code may be incorporated into the GPLv3-distributed combined
project, but its original attribution and MIT notice remain applicable to the
upstream-derived material.

The project-level GPL license therefore does not mean that every historical
source fragment originated under GPL.

---

## Mixed-origin files

A source file may contain both:

1. original Agon Extender code; and
2. material derived from an upstream project.

Such a file should retain enough information to make both origins clear.

A typical mixed-origin header may therefore contain:

```text
SPDX-License-Identifier: GPL-3.0-only

Portions derived from FabGL/vdp-gl.
Copyright (c) 2019-2022 Fabrizio Di Vittorio.
See LICENSING.md for provenance and licensing details.
```

This is only a template. Existing upstream notices should be preserved rather
than replaced with shorter wording when the original notice itself is required
or useful for provenance.

---

## Unchanged third-party files

An unchanged third-party file should normally retain its original license
header and SPDX identifier rather than being relabeled with the project's
default license.

For example, an unchanged upstream file offered as `GPL-3.0-or-later` should
remain identified as such.

The repository-wide `GPL-3.0-only` policy applies to the combined Agon Extender
work; it is not an instruction to falsify the licensing history of vendored or
unchanged upstream source.

---

## Other third-party software

Future versions of Agon Extender may use additional libraries, firmware
components, examples, generated assets, test data, fonts, or other third-party
material.

Each such component must be reviewed before redistribution.

Third-party material should:

- retain its required copyright and attribution notices;
- retain or accompany its applicable license terms;
- be compatible with distribution of the combined project under GPLv3;
- be documented when its provenance or license is not obvious from the file
  itself.

Do not assume that the presence of this `LICENSING.md` overrides a third-party
license.

---

## File-header policy

For new project-original source files, prefer a short SPDX header:

```text
SPDX-License-Identifier: GPL-3.0-only
```

A project copyright notice may also be included when appropriate.

For upstream-derived files, retain the upstream copyright/provenance
information in addition to the applicable SPDX identifier.

For unchanged upstream files, preserve the upstream license identifier and
notice.

Documentation, scripts, tests, and other repository content are covered by the
project's `GPL-3.0-only` license unless they carry an explicit different
license.

---

## Contributions

Unless explicitly agreed otherwise before contribution, contributions to Agon
Extender are accepted under the license applicable to the file being modified.

For project-original GPLv3-only files, that means contributions are made under
`GPL-3.0-only`.

Contributors should not submit code for which they do not have the right to
grant the required license.

---

## Redistribution checklist

Before a public release, verify that:

- a root `LICENSE` file contains the complete GNU GPL version 3 text;
- project-original source has appropriate `GPL-3.0-only` identification;
- FabGL/vdp-gl-derived material retains Fabrizio Di Vittorio attribution and
  its upstream provenance;
- Agon VDP-derived material retains its applicable MIT notice;
- other third-party material has been identified and its license requirements
  preserved;
- source corresponding to distributed GPL-covered binaries is provided as
  required by GPLv3.

---

## Upstream references

FabGL:

- https://github.com/fdivitto/FabGL
- http://www.fabgl.com/

Agon Platform VDP:

- https://github.com/AgonPlatform/agon-vdp

GNU General Public License version 3:

- https://www.gnu.org/licenses/gpl-3.0.html

SPDX license identifiers:

- `GPL-3.0-only` — GNU GPL version 3 only
- `GPL-3.0-or-later` — GNU GPL version 3 or any later version
- `MIT` — MIT License
