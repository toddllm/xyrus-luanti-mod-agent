# GitHub Actions Investigation - Exit Code 128

## Issue Summary
The Claude Code Review workflow was working fine but now fails with exit code 128 during the preparation phase.

## Most Likely Causes (since it was working before)

### 1. Token Expiration
- The `CLAUDE_CODE_OAUTH_TOKEN` might have expired
- Check: Go to https://github.com/toddllm/luanti-voyager/settings/secrets/actions
- Verify the token is still valid and hasn't expired

### 2. Beta Action Changes
- The action uses `anthropics/claude-code-action@beta`
- Beta actions can have breaking changes without notice
- Consider pinning to a specific commit hash instead of `@beta`

### 3. Repository Permissions
- GitHub might have changed default permissions
- The repository might have new branch protection rules
- Check: Repository Settings → Actions → General → Workflow permissions

## Quick Fixes to Try

### 1. Regenerate the Token
```
1. Go to your Claude/Anthropic dashboard
2. Generate a new OAuth token
3. Update the secret in GitHub: Settings → Secrets → Actions → CLAUDE_CODE_OAUTH_TOKEN
```

### 2. Pin the Action Version
Instead of:
```yaml
uses: anthropics/claude-code-action@beta
```

Use a specific commit (check the action's repo for a stable commit):
```yaml
uses: anthropics/claude-code-action@<commit-hash>
```

### 3. Check Repository Settings
Ensure these are enabled in Settings → Actions → General:
- Allow all actions and reusable workflows
- Read and write permissions
- Allow GitHub Actions to create and approve pull requests

### 4. Test with a Simple Workflow
Create a minimal test workflow to isolate the issue:
```yaml
name: Test Claude Action
on: workflow_dispatch
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "Testing Claude action..."
```

## The Original Working Configuration
Since it was working before, the original configuration should be correct. The issue is likely external (token, action updates, or GitHub changes) rather than the workflow file itself.