---
name: install-dependabot
description: Install and configure Dependabot for automated dependency updates in the project. Use when setting up a new dev environment, repository, adding dependency management, or asked to "install dependabot" or "set up automated updates".
---

1. Check if `.github/dependabot.yml` already exists in the project.
2. If `.github/dependabot.yml` does not already exist, create it.
   - For your reference, here is a minimal dependabot.yml file that monitors npm dependencies daily:
   ```yaml
   version: 2
   updates:
   - package-ecosystem: "npm"
      directory: "/"
      schedule:
         interval: "daily"
   ```
   - Be diligent in ensuring the `version` key in the yaml file is the latest version (use the "Additional resources" linke below to check for this). If the version is outdated, update it to the latest version.
3. Populate `.github/dependabot.yml` with the corret configuration for the project's dependencies. Here is a common use cases you will encounter (but this is listed just as an example, it is not exhaustive so refer to the "Additonal resources" if other dependencies are in scope):
   - Search the root of the project, and all subdirectories recursively, for `package.json` files. For each `package.json` file found, add an entry for `npm` dependencies in the `.github/dependabot.yml` file with the correct directory path to the `package.json` file. For example, if a `package.json` file is found in the root of the project, in a `client` directory, and in a `cdk` directory, the dependabot.yml file should have 3 entries for npm dependencies with the correct directory paths:
   ```yaml
   updates:
     - package-ecosystem: "npm"
       directory: "/"
       schedule:
         interval: "daily"
     - package-ecosystem: "npm"
       directory: "/cdk"
       schedule:
         interval: "daily"
     - package-ecosystem: "npm"
       directory: "/client"
       schedule:
         interval: "daily"
   ```
   - As of 02/08/2026, the full list of languages/technologies supported are: Bazel, Bundler, Bun, Cargo, Composer, Devcontainers, Docker, Docker Compose, Dotnet SDK, Elm, GitHub Actions, Gitsubmodule, Gomod (Go Modules), Gradle, Helm, Hex (Hex), Julia, Maven, NPM and Yarn, NuGet, OpenTofu, Pip, Pub, Swift, Terraform, UV. But you should always double check the "Additional resources" link below for the most up to date list of supported languages and technologies.

## Additional resources
- For the complete YAML spec, see https://docs.github.com/en/code-security/concepts/supply-chain-security/about-the-dependabot-yml-file
- For a list of all options and the technologies supported, see https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference