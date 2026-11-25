# Chutoro delivery releases

This public repository distributes native Chutoro delivery binaries. Application
source remains in the private `chutoroAI/chutoro` repository. No Python, pip, or
Go installation is required on end-user computers.

Chutoro's MCP connection offers setup in Codex. After the user consents, Codex
downloads the matching release and verifies its signed build provenance **before
executing it**. A trusted GitHub CLI with `gh attestation verify` is required for
this bootstrap. Verification must match all of:

- Repository: `chutoroAI/chutoro-releases`
- Signer workflow: `chutoroAI/chutoro-releases/.github/workflows/delivery-release.yml`
- Source ref: `refs/tags/delivery-vVERSION`, where VERSION is the selected release
- GitHub-hosted runner (reject self-hosted attestations)

Use the exact verification arguments supplied by the Hub. A checksum from a
download server alone is not proof of publisher identity. Do not execute a
download if verification fails. Checksums accompanying a release are for file
inventory; signed provenance is the authenticity check.

## Supported targets

| OS | CPUs | Startup |
| --- | --- | --- |
| macOS | amd64, arm64 | Per-user launchd agent |
| Windows | amd64, arm64 | Per-user Task Scheduler task |
| Linux | amd64, arm64 | systemd user service |

Codex must support its shared local App Server and queued input. Windows needs
a native `codex.exe`, a version supporting AF_UNIX, and a sufficiently short
CODEX_HOME socket path. Linux needs a working systemd user session. WSL is a
separate Linux installation. Embedded Codex servers and phone-only sessions are
not reached by this helper.

GitHub provenance signatures are not Apple notarization or Windows Authenticode
certificates. Do not disable Gatekeeper, SmartScreen, or organizational policy
to install a release. Native OS signing can be added as a separate release gate.

## Publisher setup

Configure `DELIVERY_SOURCE_TOKEN` as a fine-grained token scoped only to the
private `chutoroAI/chutoro` repository, with Contents read permission. Never use
an unrestricted personal login token or grant write access to the source.
Deploy keys are disabled by the source repository policy; keep that policy intact. Only repository administrators who already
have source access should manage this secret or edit the release workflow.

The public workflow checks out the matching `delivery-vMAJOR.MINOR.PATCH` tag
from the private source repository. Create the reviewed source tag first, then
the matching tag in this repository. Both tags should be protected from updates
and deletion. Disable Actions for untrusted forks and protect workflow changes.

The workflow runs tests on macOS, Linux and Windows, cross-compiles six binaries,
and signs their build provenance using GitHub OIDC. No source archives or build
caches are uploaded. Public job logs can contain compiler/test diagnostics;
tests must use synthetic fixtures, never private customer data.

Successful builds create a **draft** release. Verify all six assets and their
attestations, complete native installation/uninstallation acceptance tests, then
publish the release. Configure `HUB_DELIVERY_VERSION=MAJOR.MINOR.PATCH` on the Hub
only after publication. A missing release configuration disables enrollment
offers. There are no automatic updates; upgrades require another verified binary
and reuse the existing enrollment.
