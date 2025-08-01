# How to Contribute

Thank you for taking the time and effort to read this guide! Your contributions are valuable, and we appreciate your interest in improving our project.

## Getting Started

Before you start contributing, it's essential to familiarize yourself with the codebase. Spend some time reading the existing code to understand the current style and structure. This will help you align your contributions with the project's conventions and optimize for readability.

## Development Environment

To ensure a consistent development environment, we recommend using the [devcontainer](https://code.visualstudio.com/docs/devcontainers/containers) or a [GitHub Codespace](https://github.com/codespaces). These tools will provide you with a standardized setup that matches the project's requirements.

If you prefer using a local development environment, you can create a Python virtual environment using the `scripts/setup_env.sh` script. This script uses [uv](https://docs.astral.sh/uv) to manage dependencies and environment settings. It will also install required `npm` tools.

```sh
./scripts/setup_env.sh
```

### Pre-Commit Hook

We use a [pre-commit](https://pre-commit.com) hook to help identify simple issues before submitting your code for review. This ensures that your code meets the project's quality standards and reduces the chances of encountering avoidable errors during the review process.

## Submitting Changes

Changes should be proposed through a pull request (PR). When creating a PR, please include the following:

- A summary of the changes you are proposing.
- Links to any related issues.
- Relevant motivation and context for the changes.

This information helps reviewers understand the purpose of your changes and facilitates a smoother review process.

### Adding Tests

To ensure the stability and reliability of the codebase, please include tests with your pull request. We use [pytest](https://pytest.org/) for testing. To run the test suite, simply execute:

```sh
pytest tests
```

Adding tests helps verify that your changes work as intended and do not introduce new issues.

## Reporting Issues

If you encounter a bug, have a feature request, or a general question, please use the appropriate issue template provided in the repository. When submitting an issue, it is important to fill out all fields in the template. This ensures we have all the necessary information to reproduce bugs, assess feature requests, or answer questions effectively. Incomplete issues may take longer to address due to insufficient information.

Thank you for contributing! Your efforts help us maintain a high-quality codebase and make the project better for everyone.

Happy coding!
