---
name: amba
description: Analyze AMBA interface signals in Verilog, SystemVerilog, or HDL embedded in Ruby/Perl/PHP wrappers. Identify AXI, LPI Q-Channel/P-Channel interfaces, optional side-channels, and minimum spec revision. Also generates quick-reference markdown from PDFs. Trigger when user mentions AXI, AMBA, AHB, APB, Q-Channel, P-Channel, AWVALID, ARVALID, or asks to analyze a port list, interface signals, or AMBA compliance.
---

# AMBA Interface Analysis Skill

## Reference Files (load as needed)

- `references/IHI0022_AXI.md` - All AXI signal tables, version history, protocol/issue mapping, detection heuristics
- `references/IHI0068_LPI.md` - Q-Channel and P-Channel signal tables, state machines, version detection

Load reference files before doing any signal classification or version detection.

## Workflow

### 1. Extract HDL from Wrappers

Strip wrapper syntax before parsing ports:

- **Ruby/ERB**: remove `<% %>` / `<%= %>` blocks; treat `#{signal_name}` as literal signal name
- **Perl**: strip heredoc delimiters; treat `$signal_name` / `${signal_name}` as literal names
- **PHP**: strip `<?php ?>` / `<?= ?>` blocks; extract string literals containing port declarations

### 2. Extract Port List

Scan for `module ... ( ... );` declarations. Extract each port as `{direction, width, name}`.

Common prefix/suffix patterns to normalize before matching:
- Strip prefixes: `m_axi_`, `s_axi_`, `m00_axi_`, `s00_axi_`, `maxi_`, `saxi_`
- Strip suffixes: `_i`, `_o`, `_t`, `_q`, `_w`, `_next`

### 3. Classify Signals

Read `references/IHI0022_AXI.md` and `references/IHI0068_LPI.md`. Match normalized port names against signal tables. Group by channel (AW, W, B, AR, R, AC, CR, Q-Channel, P-Channel, interface-level).

### 4. Identify Interface and Version

Use the **Protocol Version to Issue Mapping** table in `qref/IHI0022_AXI.md`:
- WID on W channel -> AXI3
- AWLEN 8-bit, no WID -> AXI4+
- AWDOMAIN / AWSNOOP -> AXI5/ACE5
- Credited transport signals -> Issue J+

Use **Version Detection Heuristic** in each qref file for fine-grained issue estimation.

### 5. Identify Optional Extensions

From `qref/IHI0022_AXI.md` signal tables, note which optional extensions are present (MTE, Poison, Trace, Stash, MMU, MPAM, MEC, ACT, Credited transport, etc.).

### 6. Report

```
== AMBA Interface Analysis ==

File: <path>  [wrapper type if applicable]

Interfaces detected:
  <interface class> <Manager|Subordinate>

Channels present:
  [x] AW  mandatory: AWVALID, AWADDR  optional: AWID, AWLEN, AWQOS...
  [x] W   ...
  [x] B   ...
  [x] AR  ...
  [x] R   ...
  [ ] AC/CR  not present

Optional extensions: QoS, Memory Tagging, Poison ...

Protocol: AXI4. Minimum issue: E  (AWQOS signals Issue E+)

Warnings:
  - WID present: AXI3 signal, removed in AXI4
  - AWLEN appears 4-bit: AXI3 encoding (AXI4 requires 8-bit)
```

### 7. PDF to Quick-Reference Generation

When asked to process a new spec PDF:
1. Read signal table appendix (usually titled "Signal list")
2. Extract: name, width, source direction, description, first version present
3. Generate compressed markdown to `qref/IHI<num>_<name>.md`
4. Format: tables only (no prose), version history at top, state machines if applicable, detection heuristic at bottom

## Warnings to Emit

| Condition | Warning |
|-----------|---------|
| WID present | AXI3 signal - removed in AXI4 |
| AWLEN appears 4-bit | Possible AXI3 (AXI4 requires 8-bit) |
| AWVALID without AWADDR | Incomplete AW channel |
| ACVALID without CRVALID | Incomplete snoop channel |
| QREQn without QACCEPTn | Incomplete Q-Channel |
| PREQ without PSTATE | Incomplete P-Channel |
| Credited transport signals without ACTIVATEREQ | Incomplete credited transport |
| Parity check signal without primary signal | Orphaned parity signal |
