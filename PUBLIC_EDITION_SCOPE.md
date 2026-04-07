# Public Edition Scope

This folder contains the public repository version of the Renewable Energy Trading node that sits around DAO Hub inside the Sampo AI OS ecosystem.

This node is published separately because it shows how DAO Hub can connect to energy-market workflows: market telemetry, synthetic price snapshots, trade creation, and route optimization for renewable energy volumes.

## Repository Focus

This repository includes:

- a working FastAPI backend for authentication, market snapshots, trades, and optimization
- a lightweight stochastic market simulator for renewable generation, demand, pricing, and carbon intensity
- optional non-blocking telemetry push hooks to DAO Hub
- Docker runtime files and local development setup
- a lightweight automated test suite for the public API surface

## Repository Boundary

This repository focuses on the backend trading and market-analytics surface rather than packaging every surrounding ecosystem component.

## Narrative Role

In public ecosystem terms:

- DAO Hub remains the orchestration center
- this repository is one energy-market subsystem around that center
- both were developed within Sampo AI OS

## Safety And Operational Notes

The public edition removes hard-coded production-facing secrets and uses environment-based configuration.

Market data and optimization outputs are synthetic demo analytics for portfolio review, not live trading advice or production settlement logic.
