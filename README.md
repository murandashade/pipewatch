# pipewatch

A lightweight CLI for monitoring and alerting on ETL pipeline failures with webhook support.

---

## Installation

```bash
pip install pipewatch
```

Or install from source:

```bash
git clone https://github.com/youruser/pipewatch.git && cd pipewatch && pip install .
```

---

## Usage

Monitor a pipeline command and send an alert to a webhook if it fails:

```bash
pipewatch run --name "nightly-etl" \
  --cmd "python etl/pipeline.py" \
  --webhook "https://hooks.slack.com/services/your/webhook/url"
```

Watch a log file and alert on error patterns:

```bash
pipewatch watch --file /var/log/etl.log \
  --pattern "ERROR|FAILED" \
  --webhook "https://hooks.slack.com/services/your/webhook/url"
```

List monitored pipelines and their last status:

```bash
pipewatch status
```

Example output:

```
NAME            LAST RUN              STATUS
nightly-etl     2024-03-12 02:00:01   ✗ FAILED
daily-sync      2024-03-12 06:00:00   ✓ OK
```

---

## Configuration

Store defaults in `~/.pipewatch/config.yaml`:

```yaml
webhook: "https://hooks.slack.com/services/your/webhook/url"
retry: 3
timeout: 30
```

---

## License

MIT © 2024 [youruser](https://github.com/youruser)