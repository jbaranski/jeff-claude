---
name: jeff-aws-cdk-project
description: Configure or update AWS CDK TypeScript projects with an opinionated layout, required dependencies, scripts, and .env usage. Use when a repo should contain a CDK project. CDK app code should live in a `cdk/` folder off the root of the project with strict dependency and file structure conventions.
---

This is an opinionated view for how AWS CDK projects should be configured and maintained.

## Prerequisites

Before proceeding:

1. Ensure nvm (Node Version Manager) and Node.js are installed using the `jeff-install-nodejs` skill.
2. Ensure prettier is installed using the `jeff-install-prettier` skill.
3. Use WebSearch to verify current versions:
   - "AWS CDK latest version [current-year]"
   - "TypeScript latest version [current-year]"
   - "vitest latest version [current-year]"
   - "constructs library latest version [current-year]"
   - Update all version numbers in examples below with verified versions
   - DO NOT skip this step. DO NOT guess at version numbers.

## Goals

- Enforce a single CDK app under `cdk/` at repository root
- Keep dependencies minimal and deliberate
- Require environment configuration via `.env`
- Encourage single-stack layout with construct-per-file structure
- Make build/test/deploy repeatable and auditable

## Required Layout

### Repo Structure

- CDK app must live at `cdk/` in the project root
- `cdk/bin/` contains only a single app entrypoint (e.g., `app.ts`)
- `cdk/lib/` typically contains a single stack file (e.g., `stack.ts`) (if you're explicitly asked to do something different, get confirmation about it first)
- Each construct lives in its own file under `cdk/lib/` (or `cdk/lib/constructs` if the project is huge with 30+ constructs and has multiple stacks)

### Environment Files

- `cdk/.env`
- `cdk/.env.example`

These must be used for common build/deploy arguments instead of hardcoding in the code (e.g., API Gateway rate limits, AWS account, alarm periods, allowed Cognito origins, etc.).

### Unit tests requirements

- Use vitest for unit tests
- Use `vitest.config.ts` for test configurations (like coverage thresholds, test environment, etc...)
- Unit tests must exist for all code. Include coverage reports and ensure coverage is at least 80%
- Tests must assert configuration expectations, such as:
  - Alarms configured for all infrastructure
  - API Gateway always has a rate limit enforced
  - CloudWatch log LogGroups always has a retention period set
  - Lambdas always have memory and timeout explicitly set
  - DynamoDB tables always have point-in-time recovery enabled
  - IAM roles have least-privilege permissions and no \* references to refer to actions or resources (unless that's the best practice way for a specific service or permission)
  - etc...

- Use a dedicated test folder to scale cleanly:
  - `cdk/test/` for unit tests
  - `cdk/test/constructs/` for construct tests
  - `cdk/test/stack/` for stack-level assertions

- Example `stack.test.ts`:

```typescript
import { describe, it, expect } from 'vitest';
import { App } from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import { MyAppStack } from '../../lib/stack';

describe('MyAppStack', () => {
  it('applies API Gateway rate limits', () => {
    const app = new App();
    const stack = new MyAppStack(app, 'TestStack');
    const template = Template.fromStack(stack);

    template.hasResourceProperties('AWS::ApiGateway::Stage', {
      MethodSettings: [
        {
          ThrottlingRateLimit: 10,
          ThrottlingBurstLimit: 20
        }
      ]
    });
  });
});
```

- Best‑Practice Notes
  - Keep tests close to what you assert (e.g., API Gateway throttling, alarms, IAM policies)
  - Use `Template.fromStack` for deterministic assertions of CFN config
  - Keep coverage focused on `lib/` and `bin/` to avoid noise
  - Prefer vitest run --coverage in CI for reproducible results

## Package.json

### Dependencies

Only these are required by default. Any additional pinned dependency must be scrutinized or confirmed with the user.

Use a WebSearch to replace `<latest stable>` below with the actual latest version numbers. Do not skip or guess at version numbers, always use the WebSearch to verify.

```json
"dependencies": {
  "aws-cdk-lib": "<latest stable>",
  "constructs": "<latest stable>",
  "dotenv": "<latest stable>"
},
```

### Dev dependencies

This is less strict but still be deliberate and do not introduce unnecessary dependencies.

Also always include `source-map-support` as a `devDependencies` for better error stack traces in CDK apps, it's only used for test/dev situations and won't be part of the production build so it should be a dev dependency:

```json
"devDependencies": {
  ...
  "source-map-support": "<latest stable>"
  ...
}
```

### Scripts

Prefer npx cdk or local cdk scripts; do not rely on global install.

The `scripts` section in `package.json` should include helpful commands like the following (always include a command that will build + deploy in one step, and a command that will clean + build + deploy in one step):

```json
"scripts": {
  "build": "tsc",
  "watch": "tsc -w",
  "deploy": "npm run build && cdk deploy",
  "diff": "cdk diff",
  "synth": "cdk synth",
  "destroy": "cdk destroy",
  "clean": "rm -rf dist",
  "clean:all": "rm -rf dist node_modules",
  "test": "vitest",
  "test:run": "vitest run",
  "test:coverage": "vitest run --coverage"
}
```

## CDK App Code

### Entrypoint

App Entrypoint (`cdk/bin/app.ts`)

Only one app entrypoint is allowed. It should follow this pattern:

```
import * as cdk from 'aws-cdk-lib';
import * as dotenv from 'dotenv';
import * as path from 'path';
import { MyAppStack } from '../lib/stack';

// This works whether you run from repo root or cdk/.
dotenv.config({ path: path.resolve(__dirname, '..', '.env') });

const app = new cdk.App();

new MyAppStack(app, 'MyAppStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
    // ...other args too
  }
});
```

### Stack file

Only one stack file is typical, but leave room for more if needed or requested (but always double check if really necessary as that is non-standard).

```
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';

export class MyAppStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);
    // refer to constructs part of the stack
  }
}
```

### Constructs

Each construct should be in its own file.

Example lambda construct:

```
import { Construct } from 'constructs';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';

interface Lambda1ConstructProps {
  myTable: dynamodb.Table;
}

export class Lambda1Construct extends Construct {
  constructor(scope: Construct, id: string, props: Lambda1ConstructProps) {
    super(scope, id);
  }
}
```

Example DynamoDB construct:

```
import { Construct } from 'constructs';

export class DynamoDBConstruct extends Construct {
  constructor(scope: Construct, id: string) {
    super(scope, id);
    // tables, indexes, etc...
  }
}
```

It's ok to combine multiple Lambda functions in the same Lambda construct file if they are closely related in business purpose. Same idea applies to other resources (multiple DynamoDB tables can all live in the same construct file if they are closely related in business purpose). But typically do not mix resources in a single construct file (like mixing Lambda and DynamoDB resources in the same construct file).

## GitHub Actions

- Create a GitHub action workflow for the CDK that does a clean build + deploy (so run a build, the tests, assert coverage requirements met, synth, build, deploy, etc.) and ensure it runs on every push to main.
- The GitHub action should run the unit tests and enforce code coverage requirements on every PR push.

## Additional resources

- For complete API details, see [reference.md](reference.md)
