# Progress

Updated: 2026-11-04. Research status: R0_PARTIAL; source/data/metric audits executed; no retrieval experiments executed.

| Phase | Status | Completion evidence / next gate |
|---|---|---|
| Preserve protocol and factorial | Complete | Byte-identical copies and SHA256 manifest |
| Factorial preregistration structure | Validated | 144 unique configurations, five factor dimensions |
| Repository and skills | Complete | Private GitHub repository published; ARIS, 12 HKUSTDial skills, Graphify installed; dependency check passed |
| R0 source, paper, license audit | Partial | Upstream frozen; dataset counts/IDs and metric discrepancy checked; licenses and remaining papers unresolved |
| R1 native environment | Provisioning blocked | CUDA GPU found (8 GB); WSL install requires administrator; C: has only ~7 GB free |
| R2 numeric reproduction | Not run | Full metrics and parity/discrepancy report |
| C fixed candidates | Not run | Candidate recall, ceiling, immutable cache |
| F factorial development | Not run | Frozen group splits and dev-only selection |
| Final lockbox/external evaluation | Locked / not created | Freeze winner before one-time evaluation |

Next: resolve disk space and administrator installation of WSL, then test Linux CUDA and exact Python 3.11.5 author environment. See reports/setup_status.md and reports/reproduction_audit.md. January 4, 2027 ARR deadline independently confirmed from official ACL call. No repaired code or benchmark score exists yet.
