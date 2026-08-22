# Schedulers

The scheduler only triggers a refresh command. It does not become the source
of truth. Add equivalent definitions for systemd-user, cron, Windows Task
Scheduler, or GitHub Actions while preserving the same command contract.
