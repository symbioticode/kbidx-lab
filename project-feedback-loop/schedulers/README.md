# Schedulers

The scheduler only triggers a refresh command. It does not become the source
of truth. Add equivalent definitions for systemd-user, cron, Windows Task
Scheduler, or GitHub Actions while preserving the same command contract. The
repository currently includes systemd-user and Windows examples.

The command contract is:

```text
python kit/refresh.py examples/minimal
```

Every adapter should run the complete pipeline rather than render a previously
generated registry.
