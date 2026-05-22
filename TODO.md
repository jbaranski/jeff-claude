# TODO

## Ansible Galaxy collection auto-updates

Dependabot does not support the `ansible-galaxy` ecosystem, so collection versions
pinned in `requirements.yml` are not automatically updated.

**Discuss:** Evaluate Renovate Bot as an alternative. Renovate has a community-maintained
Ansible Galaxy preset that can open PRs when collection versions are updated on Galaxy.

Key questions to answer before adopting:
- Which collections are pinned and how frequently do they release?
- Is the update churn worth the automation overhead?
- Does Renovate fit alongside the existing Dependabot setup, or replace it entirely?

Reference: https://docs.renovatebot.com/modules/manager/ansible-galaxy/
