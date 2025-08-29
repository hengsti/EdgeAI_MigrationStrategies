## Starting a simulation run

```python
python main.py
```

## Simulation Configuration

The following options control the simulation behavior. These settings are found in the `config.yaml` file.

### Basic Simulation Options

| Key            | Description                                                   |
|----------------|---------------------------------------------------------------|
| `steps`        | Number of simulation steps (timesteps) to run                 |
| `tick_duration`| Duration of one simulation step                               |
| `tick_unit`    | Unit of time per step (e.g., `seconds`)       |

---

### Strategy Selection

| Key           | Description                                                             |
|----------------|------------------------------------------------------------------------|
| `strategy`     | Simulation strategy to use (`proactive`, `reactive`, or `oracle`)      |
| `offloading`   | Type of offloading to perform (`model` or `data`)                      |
| `topology`     | Simulation environment (`test` or `prod`)                              |

---

### Load Balancing

| Key              | Description                                                        |
|------------------|--------------------------------------------------------------------|
| `loadbalancing`  | Enables load balancing between edge devices (`true` or `false`)    |

---

### Logging & Output

| Key           | Description                                                                                  |
|---------------|----------------------------------------------------------------------------------------------|
| `info`        | Enables high-level informational logs (`true` or `false`)                                    |
| `debug`       | Enables detailed debug logs for troubleshooting (`true` or `false`)                          |
| `format_logs` | Formats and saves simulation metrics and logs to structured output files (`true` or `false`) |

---

### Energy Simulation

| Key                 | Description                                                                  |
|---------------------|------------------------------------------------------------------------------|
| `compute_energydata`| If `true`, computes energy input from solar and wind data from scratch       |