# P2P Swarm Liquidator

## Problem

Liquidations in DeFi lending protocols are highly competitive and non-deterministic.

MEV bots frontrun liquidation transactions, capturing most of the profit while:

* honest participants fail to execute
* liquidation order becomes unpredictable
* protocols risk inefficient or delayed liquidations

In volatile markets, this leads to:

* missed liquidation windows
* bad debt accumulation
* unfair profit extraction by MEV actors

## Solution

P2P Swarm Liquidator introduces deterministic liquidation ordering using a small consensus swarm.

Instead of competing in the mempool, multiple agents:

1. independently detect liquidation opportunities
2. reach agreement on execution order using Vertex BFT
3. commit the agreed order via multi-signature execution

This removes race conditions and replaces them with coordinated execution.

## Architecture

```text
Agents (3 nodes)
      ↓
Detect liquidation opportunities
      ↓
Vertex BFT consensus
      ↓
Agreed liquidation order
      ↓
Multisig execution
      ↓
On-chain liquidation
```

## Why This Matters

* Eliminates mempool race conditions
* Reduces MEV extraction from liquidation flows
* Enables predictable and fair liquidation execution
* Improves protocol safety during market volatility

## Key Features

* Deterministic liquidation ordering
* BFT-based coordination (Vertex)
* Multi-agent validation
* Reduced reliance on gas wars

## Demo

[Add your video link here]

## Repository

https://github.com/rudimentall1/p2p-swarm-liquidator

## Future Work

* Expand swarm size dynamically
* Integrate with real lending protocols
* Add economic incentives for agents
* Handle adversarial agents in consensus
