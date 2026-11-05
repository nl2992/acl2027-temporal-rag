# Progress

Updated: 2026-11-04. Research status: R0_PARTIAL; source/data/metric audits executed; no retrieval experiments executed.

| Phase | Status | Completion evidence / next gate |
|---|---|---|
| Preserve protocol and factorial | Complete | Byte-identical copies and SHA256 manifest |
| Factorial preregistration structure | Validated | 144 unique configurations, five factor dimensions |
| Repository and skills | Complete | Private GitHub repository published; ARIS, 12 HKUSTDial skills, Graphify installed; dependency check passed |
| R0 source, paper, license audit | Partial | Upstream frozen; dataset counts/IDs and metric discrepancy checked; licenses and remaining papers unresolved |
| R1 native environment | Native pins conflict; repaired setup verified | Linux/Python 3.11.5/PyTorch 2.3.1 CUDA calculation and pip check pass; disclosed Notebook repair |
| R2 numeric reproduction | Not run | Full metrics and parity/discrepancy report |
| C fixed candidates | Not run | Candidate recall, ceiling, immutable cache |
| F factorial development | Not run | Frozen group splits and dev-only selection |
| Final lockbox/external evaluation | Locked / not created | Freeze winner before one-time evaluation |

Next: repair dataset placement and relative imports in the separate repaired track; run tiny smoke tests and measure GPU feasibility. Disk space restored; Linux and CUDA execution verified. Original runner attempted under repaired dependencies and failed at dataset path resolution before retrieval. See reports/setup_status.md. No benchmark score exists yet.
