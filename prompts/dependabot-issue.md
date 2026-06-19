# Dependabot Batch Update Process

Consolidate all open Dependabot PRs into a single feature branch.

---

## Key Process Steps

**Initial Setup:**
The guidance establishes creating a dedicated feature branch (e.g., `chore/dependabot-batch-<date>`) to collect all dependency updates before merging to `main`.

**Angular-Specific Sequencing:**
Within npm sub-projects, Angular receives priority treatment: "Before touching ANY other npm dependency in this sub-project, update Angular itself first" using the official upgrade guide and `ng update` commands. Only after Angular stabilizes should dependent packages and then independent updates be applied.

**Multi-Ecosystem Independence:**
The document clarifies that "There is NO required ordering between tracks — the backend (Go modules, etc.) can be updated before, after, or alongside the frontend," meaning different technology stacks within one repository can be updated in parallel.

**Failure Handling:**
When builds break, the approach involves methodically isolating the problematic dependency through systematic reverting, then excluding only that specific update while retaining others.

**Completion:**
The process concludes with documenting results per sub-project, closing successful Dependabot PRs, and merging the consolidated branch, while leaving unsuccessful updates open for future attention.

---

## Checklist

### Setup
- [ ] Create a dedicated feature branch (e.g. `chore/dependabot-batch-<date>`)
- [ ] List all open Dependabot PRs and group them by ecosystem (npm, Go, etc.)

---

### npm Sub-Projects (per sub-project, e.g. `apps/web/`)

**Angular first (if an Angular update is open):**
- [ ] Apply the Angular update first using `ng update` and the official upgrade guide
- [ ] Verify Angular is stable before touching any other npm dependency

**Compatibility check (required even if no Angular update is open):**
- [ ] Check the Angular update guide and release notes for the current Angular major version
- [ ] For every non-Angular npm package being updated, confirm it is compatible with the installed Angular version
- [ ] Document findings by producing this table before writing any code:

    | Package | Old -> New | Angular conflict? | Notes |
    |---------|------------|-------------------|-------|
    | ...     | ...        | Yes / No          | ...   |

- [ ] Skip any package where a confirmed conflict exists; leave its Dependabot PR open

**Apply remaining updates:**
- [ ] Apply all compatible non-Angular npm updates

---

### Other Ecosystems (Go, Python, etc.)
- [ ] Apply updates independently — no required ordering relative to npm

---

### Testing
- [ ] Run `make test` and `make lint` for each affected sub-project
- [ ] If tests fail, revert only the offending package and leave its PR open
- [ ] Document which packages passed and which were excluded

---

### Closure
- [ ] Close each Dependabot PR whose update was successfully applied
- [ ] Leave open any PR whose update was skipped or caused failures
- [ ] Comment on each skipped PR explaining why it was excluded
- [ ] Push the consolidated branch
