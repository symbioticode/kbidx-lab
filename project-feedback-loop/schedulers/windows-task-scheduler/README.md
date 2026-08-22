# Windows Task Scheduler

Create a daily task that runs from the repository root:

```powershell
py .\kit\refresh.py .\examples\minimal
```

Use the user's actual repository path and Python launcher. A reusable wrapper is
provided in [`refresh.ps1`](refresh.ps1):

```powershell
pwsh -File .\schedulers\windows-task-scheduler\refresh.ps1 `
  -RepositoryRoot C:\path\to\project-feedback-loop
```

The wrapper keeps the same command contract and is intended for Windows Task
Scheduler. It also fails if the refresh does not leave
`examples/minimal/generated/manifest.json`; the manifest is the completion
marker for the generated output set. The wrapper parses it and checks that all
five individual pipeline artifacts are declared.
