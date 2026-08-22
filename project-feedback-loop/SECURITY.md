# Security policy

## Scope

The reference kit is local and offline by design. It reads declared Markdown,
TOML, and text files and writes derived JSON, text, and HTML projections. It
does not authenticate users, call external services, or execute content from
the observed corpus.

Do not place credentials, private portfolio data, personal information, or
unreviewed knowledge-base exports in this public example repository.

## Reporting

If you find a reproducible security issue in the scripts or generated output,
please open a private security report through the repository's GitHub security
channel when available. Include the affected commit, a minimal sanitized
fixture, the command used, and the observed impact. Do not publish secrets or
private source data in a public issue.

Heuristic observations are not a security boundary. Review generated HTML and
source provenance before publishing or embedding it in another system.
