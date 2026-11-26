# Chutoro delivery releases

This public repository distributes the native Codex delivery helper and the Claude Code terminal client. Server
source remains in the private `chutoroAI/chutoro` repository. The Codex helper runs as a native binary. The Claude client uses Python 3 and its standard library.

Chutoro's MCP connection offers setup in Codex. After user consent, Codex
downloads the matching release and compares its SHA-256 with the approved hash
supplied through the trusted Chutoro MCP connection **before executing it**.

Verification uses existing OS tools: `shasum -a 256` on macOS, `sha256sum` on
Linux, or PowerShell `Get-FileHash -Algorithm SHA256 -LiteralPath` on Windows.
The full 64-character result must match (case-insensitive). No GitHub CLI is
required on user machines. Stop on errors, missing tools or a mismatch; do not
run a downloaded verifier script or disable OS security controls.

The trusted expected hash comes from the operator-approved Chutoro manifest,
not from a checksum downloaded alongside the binary. This protects against
corruption or substituted release downloads while **trusting Chutoro**. It is
not independent publisher-signature verification and does not protect against a
compromised Chutoro server or a malicious approved build.

GitHub-signed build attestations remain available for publisher audits. They are
not an end-user installation prerequisite. The native install command takes
`--sha256` with the same Chutoro-approved hash and rechecks the bytes before staging;
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
and signs their build provenance using GitHub OIDC. The native release workflow uploads only the built artifacts and release metadata. Public job logs can contain compiler/test diagnostics;
tests must use synthetic fixtures, never private customer data.

Successful builds create a **draft** release. Verify all six assets and their
attestations, complete native installation/uninstallation acceptance tests, then
publish the release. The draft includes `release-manifest.json`, generated from
all six final binaries, and `SHA256SUMS`. Review the manifest against the built
artifacts and audit provenance, then update `priv/delivery-release.json` in the Hub source and the pinned installer table in `priv/static/SETUP.md` together. The Hub bundles this approved manifest, so normal deployments require no release environment variables.

Operators may override the bundled release by setting both `HUB_DELIVERY_MANIFEST` (complete reviewed JSON) and `HUB_DELIVERY_VERSION`.
Do not fetch or refresh this manifest automatically at installation time.
Incomplete or version-mismatched overrides disable enrollment offers; absent overrides use the bundled release. There are no automatic updates; upgrades require another verified binary
and reuse the existing enrollment.

## Claude Code releases

A `claude-vMAJOR.MINOR.PATCH` tag builds a macOS/Linux client archive from four explicitly listed Python files in the public tag’s `scripts/` directory. The archive contains the shell installer, launcher, session hook, and Channels bridge. The client requires Claude Code and Python 3. Its version is independent of the Codex helper.

Sync the Claude workflow and packaging script from `distribution/` and the four reviewed client files listed in `package_claude.py` from the source repository’s `scripts/` directory. Commit them in the public repository before tagging. The workflow uses the public tag to build the archive, exercise the packaged installer and launcher, and create a draft with the archive and SHA256SUMS. Compare the archive hash with the pin in the Hub's `priv/static/SETUP.md`, verify the extracted client, and publish the release before deploying the guide that references it.

To verify an existing release, run the Claude Code client release workflow manually. Choose a ref containing the matching public client and enter the published version. This rebuilds the archive and compares both files byte-for-byte with the published assets.
