# IHI0068 AMBA Low Power Interface Quick Reference

spec: ARM IHI 0068 | latest: Issue D (2021-Sep-29)
covers: Q-Channel, P-Channel, parity-extended variants

## Specification Downloads (ARM Documentation Service)

| Issue | AMBA Gen | Title | Link |
|-------|----------|-------|------|
| A | AMBA 4 | Low Power Interface Specification (confidential, not public) | n/a |
| B | AMBA 4 | Low Power Interface Specification | [IHI0068B](https://documentation-service.arm.com/documentation/ihi0068/b?lang=en&rev=b) |
| C | AMBA 5 | AMBA Low Power Interface Specification | [IHI0068C](https://documentation-service.arm.com/documentation/ihi0068/c?lang=en&rev=c) |
| D | AMBA 5 | AMBA Low Power Interface Specification (latest) | [IHI0068D](https://documentation-service.arm.com/documentation/ihi0068/d?lang=en&rev=0) |

Local PDFs: `arm_amba_specifications/IHI0068__amba_low_power_interface_specification/<issue>/`

## Version History

| Issue | Date | Key Changes |
|-------|------|-------------|
| A | 2013-Jul | Limited initial release (confidential). |
| B | 2014-Feb | First public release. Q-Channel + P-Channel. |
| C | 2016-Sep | Second release. |
| D | 2021-Sep | Added Interface Parity Protection (parity check signals for all signals). |

## Interface Selection

| Interface | Use When |
|-----------|----------|
| Q-Channel | Simple run-stop quiescence. Clock control or simple power control. Backward compatible with AXI LPI. |
| P-Channel | Complex power scenarios with multiple state transitions. Use only if Q-Channel insufficient. |

---

## Q-Channel

Evolution of the AXI Low Power Interface (CSYSREQ/CSYSACK/CACTIVE). Backward compatible when QDENY absent.

### Q-Channel Core Signals

| Signal | Dir (vs controller) | Active | Description | Since |
|--------|---------------------|--------|-------------|-------|
| QREQn | Controller→Device | LOW | Quiescence request | B |
| QACCEPTn | Device→Controller | LOW | Quiescence acceptance | B |
| QDENY | Device→Controller | HIGH | Quiescence denial (optional) | B |
| QACTIVE | Device→Controller | HIGH | Device has pending activity | B |

Must be register-driven: QREQn (at controller), QACCEPTn and QDENY (at device).
QACTIVE may be combinational OR logic of multiple source signals.

### Parity Extended Q-Channel Signals (Issue D+, optional)

Each standard signal gets an associated check signal providing odd parity.

| Standard Signal | Check Signal | Dir |
|----------------|-------------|-----|
| QREQn | QREQCHK | Controller→Device |
| QACCEPTn | QACCEPTCHK | Device→Controller |
| QDENY | QDENYCHK | Device→Controller |
| QACTIVE | QACTIVECHK | Device→Controller |

### Q-Channel State Machine

| State | QREQn | QACCEPTn | QDENY | Device Status |
|-------|-------|----------|-------|---------------|
| Q_RUN | 1 | 1 | 0 | Operational |
| Q_REQUEST | 0 | 1 | 0 | Operational, quiescence requested |
| Q_STOPPED | 0 | 0 | 0 | Quiescent. Controller does not guarantee clock/power. |
| Q_EXIT | 1 | 0 | 0 | Clock/power restoring (impl-defined delay). |
| Q_DENIED | 0 | 1 | 1 | Device denied request, remains operational. |
| Q_CONTINUE | 1 | 1 | 1 | Controller deasserted QREQn after denial. |
| Unused | x | 0 | 1 | Illegal. |

Transitions: Q_RUN -> Q_REQUEST -> Q_STOPPED -> Q_EXIT -> Q_RUN (accepted)
             Q_RUN -> Q_REQUEST -> Q_DENIED -> Q_CONTINUE -> Q_RUN (denied)

### Q-Channel Handshake Rules

- QREQn HIGH->LOW only when: QACCEPTn HIGH and QDENY LOW (Q_RUN state)
- QREQn LOW->HIGH when: both LOW (Q_STOPPED) or both HIGH (Q_CONTINUE/Q_DENIED)
- QACCEPTn HIGH->LOW only when: QREQn LOW and QDENY LOW
- QACCEPTn LOW->HIGH only when: QREQn HIGH and QDENY LOW
- QDENY HIGH->LOW only when: QREQn HIGH and QACCEPTn HIGH
- QDENY LOW->HIGH only when: QREQn LOW and QACCEPTn HIGH

### AXI LPI Backward Compatibility Mapping

| AXI LPI Signal | Q-Channel Equivalent |
|----------------|---------------------|
| CSYSREQ | QREQn (controller drives) |
| CSYSACK | QACCEPTn (device drives) |
| CACTIVE | QACTIVE |
| (none) | QDENY (tie LOW at controller if absent) |

When connecting Q-Channel controller to AXI LPI device without denial: tie QDENY LOW at controller.

### Q-Channel Signal Subsets

- Full: QREQn + QACCEPTn + QDENY + QACTIVE
- Without denial: QREQn + QACCEPTn + QACTIVE (QDENY tied LOW at controller)
- Without QACTIVE: QREQn + QACCEPTn + QDENY (QACTIVE tied LOW at controller)
- QACTIVE-only: QACTIVE only (no handshake guarantee mechanism)
- Unused interface: QREQn tied HIGH

---

## P-Channel

For complex power management with multiple power states. Direct state enumeration via PSTATE.

### P-Channel Core Signals

| Signal | Dir (vs controller) | Active | Width | Description | Since |
|--------|---------------------|--------|-------|-------------|-------|
| PACTIVE[N-1:0] | Device→Controller | HIGH | N bits | Device activity indication (N bits, one per domain) | B |
| PSTATE[M-1:0] | Controller→Device | - | M bits | Power state request (impl-defined enumeration) | B |
| PREQ | Controller→Device | HIGH | 1 | Power state transition request | B |
| PACCEPT | Device→Controller | HIGH | 1 | Transition acceptance | B |
| PDENY | Device→Controller | HIGH | 1 | Transition denial | B |

Must be register-driven: PREQ and PSTATE (at controller), PACCEPT and PDENY (at device).
PSTATE enumerations are IMPLEMENTATION DEFINED. See Arm Power Policy Unit Specification for recommended values.

### Parity Extended P-Channel Signals (Issue D+, optional)

| Standard Signal | Check Signal |
|----------------|-------------|
| PACTIVE[N-1:0] | PACTIVECHK[N-1:0] |
| PSTATE[M-1:0] | PSTATECHK[M-1:0] |
| PREQ | PREQCHK |
| PACCEPT | PACCEPTCHK |
| PDENY | PDENYCHK |

### P-Channel State Machine

| State | PREQ | PACCEPT | PDENY | Description |
|-------|------|---------|-------|-------------|
| P_STABLE | 0 | 0 | 0 | Idle. Device in current power state. |
| P_REQUEST | 1 | 0 | 0 | Controller requests PSTATE transition. |
| P_ACCEPT | 1 | 1 | 0 | Device accepts. Transition in progress. |
| P_COMPLETE | 0 | 1 | 0 | Controller deasserts PREQ. Transitional. |
| P_DENIED | 1 | 0 | 1 | Device denies request. |
| P_CONTINUE | 0 | 0 | 1 | Controller returns PREQ LOW after denial. Transitional. |

Normal flow: P_STABLE -> P_REQUEST -> P_ACCEPT -> (P_COMPLETE) -> P_STABLE
Denied flow: P_STABLE -> P_REQUEST -> P_DENIED -> (P_CONTINUE) -> P_STABLE

### P-Channel Key Rules

- PSTATE must be stable when PREQ going HIGH is detected at device.
- Only one of PACCEPT or PDENY changes per handshake transition.
- Multiple state transitions can be made without passing through a common operational state.
- PACCEPT and PDENY reset to LOW at reset assertion.
- PREQ reset to LOW at reset assertion.

### P-Channel Reset Initialization

Controller must present current PSTATE at reset deassertion. Device samples PSTATE within t_init device clock cycles. Three valid controller behaviors:
1. PREQ LOW at reset deassertion - wait t_init then transition normally.
2. PREQ HIGH before reset deassertion - device guaranteed ready after first transition.
3. PREQ HIGH after deassertion during t_init - device interprets as second transition.

---

## Version Detection Heuristic

| Signals Present | Minimum Version |
|----------------|-----------------|
| CSYSREQ / CSYSACK / CACTIVE | AXI LPI (pre-IHI0068) |
| QREQn / QACCEPTn / QACTIVE (no QDENY) | IHI0068 B+ or AXI LPI compat |
| QREQn / QACCEPTn / QDENY / QACTIVE | IHI0068 B+ (full Q-Channel) |
| QREQCHK / QACCEPTCHK / QDENYCHK / QACTIVECHK | IHI0068 D (parity protection) |
| PACTIVE / PSTATE / PREQ / PACCEPT / PDENY | IHI0068 B+ (P-Channel) |
| PREQCHK / PACCEPTCHK / PDENYCHK | IHI0068 D (parity P-Channel) |
