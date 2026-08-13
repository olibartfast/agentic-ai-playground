# RunPod experiment checklist

1. Choose hardware from the verified model profile, including RAM, disk, and
   GPU interconnect—not GPU count alone.
2. Keep at least the model cache on persistent storage when reload cost matters.
3. Bind the inference server to `127.0.0.1`.
4. Tunnel the server from the local workstation:

   ```bash
   ssh -N -L 8080:127.0.0.1:8080 root@RUNPOD_HOST
   ```

5. Validate the endpoint, run benchmarks, save results, and terminate the GPU.

