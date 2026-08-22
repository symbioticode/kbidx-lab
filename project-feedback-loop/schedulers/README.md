# Schedulers

The scheduler only triggers a refresh command. It does not become the source
of truth. Add equivalent definitions for systemd-user, cron, Windows Task
Scheduler, or GitHub Actions while preserving the same command contract. The
repository currently includes systemd-user and Windows examples. The systemd
unit uses `/usr/bin/env` so distributions such as NixOS can resolve their own
Python installation; adapt the unit if `env` is installed elsewhere.

The command contract is:

```text
python kit/refresh.py examples/minimal
```

Every adapter should run the complete pipeline rather than render a previously
generated registry. The supplied adapters also require the generated
`manifest.json` completion marker before reporting success.
