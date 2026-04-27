# TODO

- [ ] Define MVP command set for the first working CLI (core subset of DSL).
- [ ] Decide on error handling strategy (fail-fast vs. collect errors).
- [ ] Add minimal logging conventions (levels, format, output).

## runtime
- [x] Implement runtime context (hosts, ranges, groups, variables).
- [x] Add resolution helpers for names, ranges, and groups.
- [x] Create validation hooks (duplicate names, missing references).

## visitor
- [x] Create base visitor class that wires to runtime context.
- [x] Implement handlers for declarations (host/range/group/set).
- [x] Implement core actions (ping/connect/inspect/process/ping/file ops).
- [ ] Implement missing block evaluation logic (if_stmt, foreach_stmt, on_block, via_block, condition, operand).

## cli
- [x] Build REPL loop with multiline block buffering.
- [x] Implement script runner for `.ush` files.
- [x] Add consistent exit codes and error reporting.

## executor
- [x] Define distinct, Liskov-compliant interfaces for each domain (e.g., `IHttpExecutor`, `IProcessExecutor`, `IFileExecutor`, `ISystemExecutor`). Avoid a single abstract "god" interface.
- [x] Create Pure Python (platform-agnostic) executors for tasks that don't depend on the remote OS (e.g., HTTP, Ping).
- [x] Create OS-bound executors for tasks that require OS knowledge (e.g., process management, system inspection).
- [x] Implement an Executor Factory / Switcher to dynamically select the correct OS-bound implementation (Linux vs Windows) based on host configuration.
- [ ] OS-bound executors MUST wrap the Transport layer (e.g., SSH connection). The executor handles the OS logic and passes commands to the transport for execution.
- [x] Provide a no-op/mock executor for testing and early development.
- [ ] Focus initially on Linux implementations for OS-bound executors.
- [ ] base/pure
  - [x] console, http
- [ ] base/linux
  - [x] Provide skeleton for Linux executor mapping.
- [ ] base/windows
  - [x] Provide skeleton for Windows executor mapping.

## tests
- [ ] Add unit tests for parsing sample `.ush` files.
- [x] Add runtime resolution tests (groups/ranges/vars).
- [x] Add CLI tests for REPL mode.
- [x] Add CLI tests for script mode.
