# Installation bundles

No bundle is selected for normal installation yet. `current.yaml` will be created
only after hardware validation and Author acceptance. The existing bench remains
on its recorded installation; this directory does not upgrade it.

| Bundle | Role |
|---|---|
| [extender-installation-r01](bundles/extender-installation-r01/bundle.yaml) | Unselected draft package: corrected browser compression; local build checks only |

Start with the [installation guide](../docs/installing.md). Each immutable bundle
record names payload hashes and its authoritative [baseline](../docs/versions/baselines/extender-installation-r01.yaml).
Binaries and corresponding sources are generated under ignored `dist/production/`;
no public binary download has been published. An operator needs the named archives
and checksums, not access to an agent's private directory.

The package builder copies pinned canonical inputs. Never edit an extracted
package to create another candidate; change maintained inputs and allocate the
next bundle revision. [RELEASE-001](../docs/tasks/RELEASE-001.md) owns remaining
packaging validation, bench acceptance and promotion.
