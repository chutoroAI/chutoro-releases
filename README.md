# Chutoro delivery releases

This public repository distributes native Chutoro delivery binaries. Application
source remains in the private `chutoroAI/chutoro` repository. No Python, pip, or
Go installation is required on end-user computers.

Chutoro's MCP connection offers setup in Codex. After user consent, Codex
downloads the matching release and compares its SHA-256 with the approved hash
supplied through the trusted Hub MCP connection **before executing it**.

Verification uses existing OS tools: `shasum -a 256` on macOS, `sha256sum` on
Linux, or PowerShell `Get-FileHash -Algorithm SHA256 -LiteralPath` on Windows.
The full 64-character result must match (case-insensitive). No GitHub CLI is
required on user machines. Stop on errors, missing tools or a mismatch; do not
run a downloaded verifier script or disable OS security controls.

The trusted expected hash comes from the Hub's operator-approved manifest,
not from a checksum downloaded alongside the binary. This protects against
corruption or substituted release downloads while **trusting the Hub**. It is
not independent publisher-signature verification and does not protect against a
compromised Hub or a malicious approved build.

GitHub-signed build attestations remain available for publisher audits. They are
not an end-user installation prerequisite. The native install command takes
`--sha256` with the same Hub-approved hash and rechecks the bytes before staging;
self-verification alone cannot establish bootstrap trust.

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
publish the release. The draft includes `release-manifest.json`, generated from
all six final binaries, and `SHA256SUMS`. Review the manifest against the built
artifacts and audit provenance, then explicitly pin its complete JSON as
`HUB_DELIVERY_MANIFEST` and its version as `HUB_DELIVERY_VERSION` on the Hub.
Do not fetch or refresh this manifest automatically at installation time.
Missing, incomplete or version-mismatched hashes disable enrollment offers. There are no automatic updates; upgrades require another verified binary
and reuse the existing enrollment.
