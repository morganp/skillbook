# AMBA Interface Analysis Skill

Analyzes Verilog and SystemVerilog RTL to identify AMBA interfaces, classify
signals by channel and protocol version, and report the minimum spec revision
required by signals present in the port list.

## Intended Use

Point Claude at a module port list or HDL file. The skill will:

1. Strip any Ruby/ERB, Perl, or PHP wrapper syntax to expose raw HDL
2. Extract and normalize port names (strips `m_axi_`, `s_axi_`, `_i`, `_o`, etc.)
3. Classify each signal against AMBA signal tables
4. Identify which interfaces are present (AXI Manager/Subordinate, Q-Channel, P-Channel, etc.)
5. Detect optional extensions (QoS, Memory Tagging, Poison, Stash, Parity, Credited Transport...)
6. Report minimum protocol version and issue letter required

### Example prompt

```
Analyze the port list in my_dma.sv and identify all AMBA interfaces,
optional extensions present, and the minimum AXI issue required.
```

### Example output

```
== AMBA Interface Analysis ==

File: my_dma.sv

Interfaces detected:
  AXI4 Manager (m_axi_* prefix)
  Q-Channel Requestor (qreqn / qacceptn / qactive)

Channels present:
  [x] AW  AWVALID, AWREADY, AWADDR, AWLEN, AWSIZE, AWBURST, AWID, AWQOS
  [x] W   WVALID, WREADY, WDATA, WSTRB, WLAST
  [x] B   BVALID, BREADY, BID, BRESP
  [x] AR  ARVALID, ARREADY, ARADDR, ARLEN, ARSIZE, ARBURST, ARID, ARQOS
  [x] R   RVALID, RREADY, RDATA, RRESP, RID, RLAST
  [ ] AC/CR  not present

Optional extensions: QoS

Protocol: AXI4. Minimum issue: E  (AWQOS present, introduced Issue E)

Q-Channel: complete (QREQn + QACCEPTn + QACTIVE)

Warnings:
  none
```

## Supported Standards

| Standard | Ref File | Status | Covers |
|----------|----------|--------|--------|
| IHI0022 AXI | `references/IHI0022_AXI.md` | **Implemented** | AXI3, AXI4, AXI4-Lite, AXI5, AXI5-Lite, ACE, ACE5 (Issues B-L) |
| IHI0068 LPI | `references/IHI0068_LPI.md` | **Implemented** | Q-Channel, P-Channel, parity extensions (Issues B-D) |

## Standards Pending Signal Tables

Signal tables not yet extracted. Stub files contain spec download links only.
Use SKILL.md step 7 to populate from the local PDFs.

| Standard | Ref File | Covers |
|----------|----------|--------|
| IHI0011 AMBA 2 | `references/IHI0011_AMBA2.md` | Original AMBA 2.0: AHB, ASB, APB |
| IHI0024 APB | `references/IHI0024_APB.md` | APB3, APB4, APB5 (Issues B-E) |
| IHI0032 ATB | `references/IHI0032_ATB.md` | ATB3, ATB4, ATB5 (Issues A-C) |
| IHI0033 AHB | `references/IHI0033_AHB.md` | AHB-Lite, AHB5 (Issues A-C) |
| IHI0050 CHI | `references/IHI0050_CHI.md` | Coherent Hub Interface (Issues B-H) |
| IHI0051 AXI-Stream | `references/IHI0051_AXIS.md` | AXI4-Stream (Issues A-B) |
| IHI0079 CXS | `references/IHI0079_CXS.md` | Coherent eXpansion Switches (Issues A-D) |
| IHI0082 ATP | `references/IHI0082_ATP.md` | Adaptive Traffic Profiles |
| IHI0083 GFB | `references/IHI0083_GFB.md` | Generic Flash Bus |
| IHI0088 DTI | `references/IHI0088_DTI.md` | Display Transfer Interface (Issues E.a-H) |
| IHI0089 LTI | `references/IHI0089_LTI.md` | Low-speed Transfer Interface (Issues A-D) |
| IHI0098 CHI-C2C | `references/IHI0098_CHI_C2C.md` | CHI Chip-to-Chip Architecture |
| DVI0045 ML-AHB | `references/DVI0045_ML_AHB.md` | Multi-layer AHB bus matrix overview |

## Wrapper Support

| Wrapper | Syntax stripped |
|---------|----------------|
| Ruby/ERB | `<% %>`, `<%= %>`, `#{signal}` |
| Perl | Heredoc delimiters, `$signal`, `${signal}` |
| PHP | `<?php ?>`, `<?= ?>`, string literal extraction |

## References

All spec PDFs stored locally under `references/arm_amba_specifications/` (gitignored).
Download links for every issue available in each standard's reference file.
