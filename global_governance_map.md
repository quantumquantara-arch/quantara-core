# Quantara Global Governance — System Map

```mermaid
flowchart TD

%% LAYERS
subgraph L1[Sensing Layer]
A1[Agent k/Δφ/Ω Telemetry]
A2[System Monitors]
A3[Eco Feedback]
end

subgraph L2[Synthesis Layer]
B1[Tensor-Logic Fusion: symbolic <-> neural <-> affect]
B2[Field Harmonizer: k flux aggregation]
B3[Conflict Resolver: minimize Δφ with Ω bounds]
end

subgraph L3[Decision Layer]
C1[Coherence Councils]
C2[Ethical Balance Index (EBI)]
C3[Policy Generator: adaptive rules]
end

subgraph L4[Action Layer]
D1[Institutional Updates]
D2[Model / Agent Tuning]
D3[Infrastructure Changes]
end

subgraph L5[Audit Layer]
E1[Telemetry Ledger: JSONL / append-only]
E2[Coherence Reports]
E3[Public Oversight API]
end

A1 --> B1
A2 --> B1
A3 --> B1
B1 --> B2 --> B3 --> C1
C1 --> C2 --> C3
C3 --> D1
C3 --> D2
C3 --> D3
D1 --> E1
D2 --> E1
D3 --> E1
E1 --> E2 --> E3

E1 -. recalibration .-> A1
E2 -. governance insight .-> C1
C2 -. thresholds/targets .-> B2

classDef mod fill:#f6f8fa,stroke:#d0d7de,color:#24292f;
I1[coherence_field/]:::mod
I2[tensor_logic/]:::mod
I3[quantara_instrumentation/]:::mod

I1 --- A1
I2 --- B1
I3 --- C2
```
