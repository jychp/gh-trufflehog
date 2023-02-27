# gh-trufflehog
Enhanced GitHub action for trufflehog

## Example 

```yaml
name: Leaked Secrets Scan
on: [pull_request]
jobs:
  TruffleHog:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        with:
          fetch-depth: 0
      - name: TruffleHog OSS
        uses: resilience-jychp/gh-trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD
```

## Whitelist

You can whitelist secrets using `.trufflehog_whitelist.yaml` file :

```yaml
whitelist:
- secret: MyDummyTestPassword
  reason: "Just a test"
```