# AWS deployment checklist

1. Select an instance from the verified model profile, including system RAM,
   GPU memory, GPU count, and interconnect requirements.
2. Use persistent storage when downloading or preparing the model is expensive.
3. Restrict inbound access with security groups; do not expose an
   unauthenticated inference port.
4. Prefer an SSH tunnel for temporary experiments.
5. Save benchmark results, then stop or terminate chargeable compute.
