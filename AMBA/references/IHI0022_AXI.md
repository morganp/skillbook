# IHI0022 AMBA AXI Quick Reference

spec: ARM IHI 0022 | latest: Issue L (2025-Aug-27)
covers: AXI3, AXI4, AXI4-Lite, AXI5, AXI5-Lite, ACE, ACE5, ACE5-Lite, ACE5-LiteDVM, ACE5-LiteACP

## Specification Downloads (ARM Documentation Service)

| Issue | AMBA Gen | Title | Link |
|-------|----------|-------|------|
| B | AMBA 3 | AMBA AXI Protocol Specification Version B | [IHI0022B](https://documentation-service.arm.com/documentation/ihi0022/b?lang=en&rev=0) |
| C | AMBA 4 | AMBA AXI Protocol Specification Version C | [IHI0022C](https://documentation-service.arm.com/documentation/ihi0022/c?lang=en&rev=1) |
| D | AMBA 4 | AMBA AXI and ACE Protocol Specification | [IHI0022D](https://documentation-service.arm.com/documentation/ihi0022/d?lang=en&rev=0) |
| E | AMBA 4 | AMBA AXI and ACE Protocol Specification Version E | [IHI0022E](https://documentation-service.arm.com/documentation/ihi0022/e?lang=en&rev=1) |
| F.b | AMBA 5 | AMBA AXI and ACE Protocol Specification Version F.b | [IHI0022F.b](https://documentation-service.arm.com/documentation/ihi0022/fb?lang=en&rev=0) |
| G | AMBA 5 | AMBA AXI and ACE Protocol Specification Version G | [IHI0022G](https://documentation-service.arm.com/documentation/ihi0022/g?lang=en&rev=0) |
| H | AMBA 5 | AMBA AXI and ACE Protocol Specification Version H | [IHI0022H](https://documentation-service.arm.com/documentation/ihi0022/h?lang=en&rev=0) |
| H.c | AMBA 5 | AMBA AXI and ACE Protocol Specification Version H.c | [IHI0022H.c](https://documentation-service.arm.com/documentation/ihi0022/hc?lang=en&rev=0) |
| J | AMBA 5 | AMBA AXI Protocol Specification (AXI5-only) | [IHI0022J](https://documentation-service.arm.com/documentation/ihi0022/j?lang=en&rev=0) |
| K | AMBA 5 | AMBA AXI Protocol Specification | [IHI0022K](https://documentation-service.arm.com/documentation/ihi0022/k?lang=en&rev=0) |
| L | AMBA 5 | AMBA AXI Protocol Specification (latest) | [IHI0022L](https://documentation-service.arm.com/documentation/ihi0022/l?lang=en&rev=0) |

Local PDFs: `arm_amba_specifications/IHI0022__amba_axi_protocol_specification/<issue>/`

## Protocol Version to Issue Mapping

Issue letters are document revision numbers. Protocol version names (AXI3, AXI4, AXI5) span multiple issues.

| Protocol | Issues | Key Discriminators |
|----------|--------|--------------------|
| AXI3 | A, B | WID on W channel; AWLEN 4-bit; AWLOCK 2-bit; no AWREGION |
| AXI4 / AXI4-Lite | C, D, E, F, G, H, H.b, H.c | AWLEN 8-bit; WID removed from W; AWREGION/AWUSER added (D+); AWQOS (E+) |
| ACE (coherent) | D, E, F, G, H, H.b, H.c | Added alongside AXI4. AWDOMAIN, AWSNOOP, AC/CR channels. |
| AXI5 / ACE5 | F, G, H, H.b, H.c | Introduced in F. AWATOP, new optional features. |
| AXI5-only spec | J, K, L | AXI3, AXI4, AXI4-Lite, ACE, ACE5 content removed from document. See IHI0022 H.c for legacy. Credited transport added (J). |

AXI4-Lite: subset of AXI4 (no burst, no IDs, no WLAST). Still documented in AXI4-era issues.
AXI5-Lite: subset of AXI5 (burst length 1, WriteNoSnoop/ReadNoSnoop opcodes only). Issue J+.

Note: Issues J+ are AXI5-only. For AXI3/AXI4 signals, refer to IHI0022 H.c or earlier.

## Version History

| Issue | Date | Key Additions |
|-------|------|---------------|
| A | 2003-Jun | First release. AXI3. 5-channel basic structure. |
| B | 2004-Mar | AXI spec v1.0 |
| C | 2010-Mar | AXI spec v2.0 |
| D | 2011-Oct | First AXI+ACE release. AXI4: AWLEN 8-bit, AWID removed from W channel, AWREGION, AWUSER/WUSER/BUSER/ARUSER/RUSER |
| E | 2013-Feb | AWQOS/ARQOS. Second AXI+ACE release. |
| F | 2017-Dec | AXI5, AXI5-Lite, ACE5, ACE5-Lite, ACE5-LiteACP. AWDOMAIN, AWSNOOP/ARSNOOP, AWATOP. |
| G | 2019-Jul | New optional features for AMBA 5 variants. |
| H | 2020-Mar | New optional features for AMBA 5 variants. AWAKEUP/ACWAKEUP. |
| H.b | 2021-Jan | Manager/Subordinate terminology (was Master/Slave). |
| H.c | 2021-Jan | Errata. |
| J | 2023-Mar | AXI3/AXI4/ACE removed. AXI5-only. Credited transport: AWPENDING/WCRDT/BPENDING/ARPENDING/RPENDING. |
| K | 2023-Sep | MEC: AWMECID/ARMECID. MPAM: AWMPAM/ARMPAM. Read chunking: ARCHUNKEN/RCHUNKV/RCHUNKNUM/RCHUNKSTRB. Unique ID: AWIDUNQ/ARIDUNQ/BIDUNQ/RIDUNQ. |
| L | 2025-Aug | ACT: AWACT/AWACTV/ARACT/ARACTV. Credited transport option. AWMMUPASUNKNOWN/AWMMUPM. GDI. Untranslated v4. CMO to PoPS. BBUSY/RBUSY. |

## Interface Classes (Issue J+)

| Class | Use Case |
|-------|----------|
| AXI5 | Generic, no constraints. Recommended for all new designs. |
| ACE5-Lite | I/O coherent agent (needs AxSNOOP). |
| ACE5-LiteDVM | System MMU receiving DVM invalidations. |
| ACE5-LiteACP | Tightly coupled accelerator. DATA_WIDTH=128 fixed. |
| AXI5-Lite | Register-based peripherals. Burst length 1 only. |

Signal matrix codes: Y=Mandatory, YM=Manager mandatory/Sub optional, YS=Manager optional/Sub mandatory, O=Optional, NS=Optional/Not present, N=Not present.

## Signal Tables

### AW - Write Request Channel (Manager→Subordinate unless noted)

| Signal | Width | Src | Description | Since |
|--------|-------|-----|-------------|-------|
| AWVALID | 1 | M | Valid | A |
| AWREADY | 1 | S | Ready | A |
| AWPENDING | 1 | M | Pending (credited transport) | J |
| AWCRDT | Num_RP_AWW | S | Credit grant (credited) | J |
| AWCRDTSH | 1 | S | Shared credit grant (credited) | J |
| AWRP | clog2(Num_RP_AWW) | M | Resource Plane indicator | J |
| AWSHAREDCRD | 1 | M | Shared credit indicator | J |
| AWID | ID_W_WIDTH | M | Transaction ID | A |
| AWADDR | ADDR_WIDTH | M | Address | A |
| AWREGION | 4 | M | Region identifier | D |
| AWLEN | 8 | M | Burst length | D (was 4b in A-C) |
| AWSIZE | 3 | M | Transfer size | A |
| AWBURST | 2 | M | Burst type | A |
| AWLOCK | 1 | M | Exclusive access | A |
| AWCACHE | 4 | M | Memory attributes | A |
| AWPROT | 3 | M | Protection attributes | A |
| AWNSE | 1 | M | Non-secure ext for RME | F |
| AWPAS | PAS_WIDTH | M | Physical Address Space | F |
| AWINST | 1 | M | Instruction request | F |
| AWPRIV | 1 | M | Privileged request | F |
| AWQOS | 4 | M | QoS identifier | E |
| AWUSER | USER_REQ_WIDTH | M | User extension | D |
| AWDOMAIN | 2 | M | Shareability domain | F |
| AWSNOOP | AWSNOOP_WIDTH | M | Write opcode | F |
| AWSTASHNID | 11 | M | Stash Node ID | G |
| AWSTASHNIDEN | 1 | M | Stash Node ID enable | G |
| AWSTASHLPID | 5 | M | Stash Logical Processor ID | G |
| AWSTASHLPIDEN | 1 | M | Stash LP ID enable | G |
| AWTRACE | 1 | M | Trace signal | H |
| AWLOOP | LOOP_W_WIDTH | M | Loopback signal | H |
| AWMMUVALID | 1 | M | MMU signal qualifier | J |
| AWMMUSECSID | SECSID_WIDTH | M | Secure Stream ID | J |
| AWMMUSID | SID_WIDTH | M | StreamID | J |
| AWMMUSSIDV | 1 | M | SubstreamID valid | J |
| AWMMUSSID | SSID_WIDTH | M | SubstreamID | J |
| AWMMUATST | 1 | M | Address translated indicator | J |
| AWMMUFLOW | 2 | M | SMMU flow type | J |
| AWMMUPASUNKNOWN | 1 | M | PAS unknown indicator | L |
| AWMMUPM | 1 | M | Protected Mode indicator | L |
| AWPBHA | 4 | M | Page-based Hardware Attributes | K |
| AWMECID | MECID_WIDTH | M | Memory Encryption Context ID | K |
| AWNSAID | 4 | M | Non-secure Access ID | K |
| AWSUBSYSID | SUBSYSID_WIDTH | M | Subsystem ID | J |
| AWATOP | 6 | M | Atomic transaction opcode | F |
| AWMPAM | MPAM_WIDTH | M | MPAM information | K |
| AWIDUNQ | 1 | M | Unique ID indicator | K |
| AWCMO | AWCMO_WIDTH | M | CMO type | J |
| AWTAGOP | 2 | M | Memory Tag operation | G |
| AWACT | ACT_W_WIDTH | M | ACT payload | L |
| AWACTV | 1 | M | ACT valid | L |

### W - Write Data Channel (Manager→Subordinate)

| Signal | Width | Src | Description | Since |
|--------|-------|-----|-------------|-------|
| WVALID | 1 | M | Valid | A |
| WREADY | 1 | S | Ready | A |
| WPENDING | 1 | M | Pending (credited) | J |
| WCRDT | Num_RP_AWW | S | Credit grant | J |
| WCRDTSH | 1 | S | Shared credit grant | J |
| WRP | clog2(Num_RP_AWW) | M | Resource Plane indicator | J |
| WSHAREDCRD | 1 | M | Shared credit indicator | J |
| WDATA | DATA_WIDTH | M | Write data | A |
| WSTRB | DATA_WIDTH/8 | M | Write strobes | A |
| WTAG | ceil(DATA_WIDTH/128)*4 | M | Memory Tag | G |
| WTAGUPDATE | ceil(DATA_WIDTH/128) | M | Memory Tag update | G |
| WLAST | 1 | M | Last write data | A |
| WUSER | USER_DATA_WIDTH | M | User extension | D |
| WPOISON | ceil(DATA_WIDTH/64) | M | Poison indicator | H |
| WTRACE | 1 | M | Trace signal | H |
| WID | ID_W_WIDTH | M | Transaction ID (AXI3 only) | A (removed D) |

### B - Write Response Channel (Subordinate→Manager)

| Signal | Width | Src | Description | Since |
|--------|-------|-----|-------------|-------|
| BVALID | 1 | S | Valid | A |
| BREADY | 1 | M | Ready | A |
| BPENDING | 1 | S | Pending (credited) | J |
| BCRDT | 1 | M | Credit grant (credited) | J |
| BID | ID_W_WIDTH | S | Transaction ID | A |
| BIDUNQ | 1 | S | Unique ID indicator | K |
| BRESP | BRESP_WIDTH | S | Write response | A |
| BCOMP | 1 | S | Completion response indicator | J |
| BPERSIST | 1 | S | Persist response | J |
| BTAGMATCH | 2 | S | Memory Tag Match response | G |
| BUSER | USER_RESP_WIDTH | S | User extension | D |
| BTRACE | 1 | S | Trace signal | H |
| BLOOP | LOOP_W_WIDTH | S | Loopback signal | H |
| BBUSY | 2 | S | Busy indicator | L |

### AR - Read Request Channel (Manager→Subordinate)

| Signal | Width | Src | Description | Since |
|--------|-------|-----|-------------|-------|
| ARVALID | 1 | M | Valid | A |
| ARREADY | 1 | S | Ready | A |
| ARPENDING | 1 | M | Pending (credited) | J |
| ARCRDT | Num_RP_AR | S | Credit grant (credited) | J |
| ARCRDTSH | 1 | S | Shared credit grant | J |
| ARRP | clog2(Num_RP_AR) | M | Resource Plane indicator | J |
| ARSHAREDCRD | 1 | M | Shared credit indicator | J |
| ARID | ID_R_WIDTH | M | Transaction ID | A |
| ARADDR | ADDR_WIDTH | M | Address | A |
| ARREGION | 4 | M | Region identifier | D |
| ARLEN | 8 | M | Burst length | D (was 4b) |
| ARSIZE | 3 | M | Transfer size | A |
| ARBURST | 2 | M | Burst type | A |
| ARLOCK | 1 | M | Exclusive access | A |
| ARCACHE | 4 | M | Memory attributes | A |
| ARPROT | 3 | M | Protection attributes | A |
| ARNSE | 1 | M | Non-secure ext for RME | F |
| ARPAS | PAS_WIDTH | M | Physical Address Space | F |
| ARINST | 1 | M | Instruction request | F |
| ARPRIV | 1 | M | Privileged request | F |
| ARQOS | 4 | M | QoS identifier | E |
| ARUSER | USER_REQ_WIDTH | M | User extension | D |
| ARDOMAIN | 2 | M | Shareability domain | F |
| ARSNOOP | ARSNOOP_WIDTH | M | Read opcode | F |
| ARTRACE | 1 | M | Trace signal | H |
| ARLOOP | LOOP_R_WIDTH | M | Loopback signal | H |
| ARMMUVALID | 1 | M | MMU signal qualifier | J |
| ARMMUSECSID | SECSID_WIDTH | M | Secure Stream ID | J |
| ARMMUSID | SID_WIDTH | M | StreamID | J |
| ARMMUSSIDV | 1 | M | SubstreamID valid | J |
| ARMMUSSID | SSID_WIDTH | M | SubstreamID | J |
| ARMMUATST | 1 | M | Address translated indicator | J |
| ARMMUFLOW | 2 | M | SMMU flow type | J |
| ARMMUPASUNKNOWN | 1 | M | PAS unknown indicator | L |
| ARMMUPM | 1 | M | Protected Mode indicator | L |
| ARPBHA | 4 | M | Page-based Hardware Attributes | K |
| ARMECID | MECID_WIDTH | M | Memory Encryption Context ID | K |
| ARNSAID | 4 | M | Non-secure Access ID | K |
| ARSUBSYSID | SUBSYSID_WIDTH | M | Subsystem ID | J |
| ARMPAM | MPAM_WIDTH | M | MPAM information | K |
| ARCHUNKEN | 1 | M | Read data chunking enable | K |
| ARIDUNQ | 1 | M | Unique ID indicator | K |
| ARTAGOP | 2 | M | Memory Tag operation | G |
| ARACT | ACT_R_WIDTH | M | ACT payload | L |
| ARACTV | 1 | M | ACT valid | L |

### R - Read Data Channel (Subordinate→Manager)

| Signal | Width | Src | Description | Since |
|--------|-------|-----|-------------|-------|
| RVALID | 1 | S | Valid | A |
| RREADY | 1 | M | Ready | A |
| RPENDING | 1 | S | Pending (credited) | J |
| RCRDT | 1 | M | Credit grant (credited) | J |
| RID | ID_R_WIDTH | S | Transaction ID | A |
| RIDUNQ | 1 | S | Unique ID indicator | K |
| RDATA | DATA_WIDTH | S | Read data | A |
| RTAG | ceil(DATA_WIDTH/128)*4 | S | Memory Tag | G |
| RRESP | RRESP_WIDTH | S | Read response | A |
| RLAST | 1 | S | Last read data | A |
| RUSER | USER_DATA_WIDTH+USER_RESP_WIDTH | S | User extension | D |
| RPOISON | ceil(DATA_WIDTH/64) | S | Poison indicator | H |
| RTRACE | 1 | S | Trace signal | H |
| RLOOP | LOOP_R_WIDTH | S | Loopback signal | H |
| RCHUNKV | 1 | S | Read data chunking valid | K |
| RCHUNKNUM | RCHUNKNUM_WIDTH | S | Read data chunk number | K |
| RCHUNKSTRB | RCHUNKSTRB_WIDTH | S | Read data chunk strobe | K |
| RBUSY | 2 | S | Busy indicator | L |

### AC/CR - Snoop Channels (DVM messages, ACE5-LiteDVM only)

| Signal | Width | Src | Description | Since |
|--------|-------|-----|-------------|-------|
| ACVALID | 1 | S | Valid | F |
| ACREADY | 1 | M | Ready | F |
| ACPENDING | 1 | S | Pending (credited) | J |
| ACCRDT | 1 | M | Credit grant | J |
| ACADDR | ADDR_WIDTH | S | DVM message payload | F |
| ACVMIDEXT | 4 | S | VMID extension | G |
| ACTRACE | 1 | S | Trace signal | H |
| CRVALID | 1 | M | Valid | F |
| CRREADY | 1 | S | Ready | F |
| CRPENDING | 1 | M | Pending (credited) | J |
| CRCRDT | 1 | S | Credit grant | J |
| CRTRACE | 1 | M | Trace signal | H |

### Interface Level Signals

| Signal | Width | Src | Description | Since |
|--------|-------|-----|-------------|-------|
| ACLK | 1 | Ext | Global clock | A |
| ARESETn | 1 | Ext | Global reset (active LOW) | A |
| ACTIVATEREQ | 1 | M | Activation request (credited) | J |
| ACTIVATEACK | 1 | S | Activation acknowledge | J |
| ASKSTOP | 1 | S | Stop request | J |
| ACTIVATEREQD | 1 | S | Activation request for snoop channels | J |
| ACTIVATEACKD | 1 | M | Activation acknowledge for snoop channels | J |
| ASKSTOPD | 1 | M | Stop request for snoop channels | J |
| AWAKEUP | 1 | M | Wakeup for read/write channels | H |
| ACWAKEUP | 1 | S | Wakeup for snoop channels | H |
| VAWQOSACCEPT | 4 | S | QoS acceptance level for write | E |
| VARQOSACCEPT | 4 | S | QoS acceptance level for read | E |
| SYSCOREQ | 1 | M | Coherency connect request | F |
| SYSCOACK | 1 | S | Coherency connect acknowledge | F |
| BROADCASTATOMIC | 1 | Tie | Control: Atomic transactions | F |
| BROADCASTSHAREABLE | 1 | Tie | Control: Shareable transactions | F |
| BROADCASTCACHEMAINT | 1 | Tie | Control: cache maintenance ops | J |
| BROADCASTCMOPOPA | 1 | Tie | Control: CleanInvalidPoPA CMO | J |
| BROADCASTPERSIST | 1 | Tie | Control: Persist CMOs | J |
| BROADCASTSTORAGE | 1 | Tie | Control: CleanInvalidStorage CMO | L |

## Minimum Version Detection Heuristic

### Protocol Version (AXI3 / AXI4 / AXI5)

| Signals / widths | Protocol version | Issues |
|-----------------|-----------------|--------|
| WID on W channel | AXI3 | A, B |
| AWLEN 4-bit wide, AWLOCK 2-bit | AXI3 | A, B |
| No WID; AWLEN 8-bit; AWREGION or AWUSER present | AXI4 | D+ |
| AWQOS / ARQOS present | AXI4 (QoS) | E+ |
| AWDOMAIN / AWSNOOP / ARSNOOP present | AXI5 or ACE5 | F+ |
| AWATOP present | AXI5 (Atomic) | F+ |
| AWPENDING / credited transport signals | AXI5 (Issue J+ spec) | J+ |

### Issue Letter (fine-grained, AXI5 era)

Signals present -> minimum issue:
- AWDOMAIN / AWSNOOP / AWATOP: **Issue F** (AXI5 introduced)
- AWSTASHNID / ACVMIDEXT / AWTAGOP: **Issue G+**
- AWAKEUP / ACWAKEUP / WPOISON / RPOISON / WTRACE: **Issue H+**
- AWPENDING / WCRDT / BPENDING / ARCRDT / RPENDING / credited transport: **Issue J+**
- AWMMUVALID / AWMMUSID / AWCMO: **Issue J+**
- AWMECID / ARMECID / AWMPAM / ARMPAM / ARCHUNKEN / RCHUNKV / AWIDUNQ: **Issue K+**
- AWACT / AWACTV / BBUSY / RBUSY / AWMMUPASUNKNOWN / AWMMUPM: **Issue L+**

## AXI4-Lite Minimal Port Set

Required: ACLK, ARESETn, AWVALID, AWREADY, AWADDR, AWPROT, WVALID, WREADY, WDATA, WSTRB, BVALID, BREADY, BRESP, ARVALID, ARREADY, ARADDR, ARPROT, RVALID, RREADY, RDATA, RRESP

Note: No AWID/ARID/BID/RID, no AWLEN/ARLEN, no AWBURST/ARBURST.

## Signal Naming Conventions

- `Ax` prefix = applies to both AR and AW channels (e.g., AxCACHE means AWCACHE and ARCACHE)
- lowercase `n` at start or end = active-LOW signal (e.g., ARESETn)
- lowercase `x` at second letter = collective term for Read and Write variants
