# Inkling profile

Inkling is retained as the high-end serving reference. It is not the default
backend for developing the OpenCode/Hermes integration.

Use a managed API first. For self-hosting, validate the exact checkpoint's
precision, supported GPU architecture, GPU count, interconnect, runtime build,
and storage footprint before renting a node. Aggregate memory across isolated
instances is not a substitute for the required intra-node topology.

