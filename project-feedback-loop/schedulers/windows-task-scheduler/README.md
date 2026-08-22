# Windows Task Scheduler

Create a daily task that runs from the repository root:

```powershell
py .\kit\registry.py .\examples\minimal\registry.toml
py .\kit\render_context.py .\examples\minimal\registry.json
```

Use the user's actual repository path and Python launcher. Contributions that
provide an importable XML task definition or a PowerShell wrapper are welcome.
