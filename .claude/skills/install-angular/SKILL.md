---
name: install-angular
description: Install the latest Angular CLI version globally. Use when setting up a dev environment, generating a new Angular or front-end project, or asked to "install Angular", "make a user interface", or "make a client application".
---

Before proceeding:
   - Ensure nvm (Node Version Manager) and Node.js are installed using the `install-nodejs` skill.


1. Run `npm install -g @angular/cli && ng update @angular/core @angular/cli` to install or update to the latest Angular CLI globally.
2. Verify installation by running `ng version` and ensure the Angular CLI version is the latest available version.
3. Create a new project by running `ng new <project-name>` and follow the prompts to set up the project with the desired configuration.
   - Use `CSS` for stylesheet format.
   - Do NOT enable server side rendering
4. Use the latest stable version of `tailwindcss` as a `devDependency`. Refer to the documentation at https://tailwindcss.com/docs.
   - To install run `ng add tailwindcss` and confirm any prompts. This is equivalent to doing the following (assert these things were done):
      - `npm install -D tailwindcss @tailwindcss/postcss postcss`
      - Configure `.postcssrc.json` with the following content:
      ```
      {
         "plugins": {
            "@tailwindcss/postcss": {}
         }
      }
      ```
      - `src/styles.css` should contain `@import "tailwindcss"`;

5. Create a `netlify.toml` file in the root of the Angular project directory with the following content:
   ```
    [[redirects]]
      from = "/*"
      to = "/index.html"
      status = 200
   ```


After complete:
   - Ensure prettier is installed using the `install-prettier` skill.
   - For further Angular development tasks (generating components, services, implementing features), use the `angular-frontend-developer` agent
