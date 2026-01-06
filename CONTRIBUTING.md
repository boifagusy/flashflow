# Contributing to FlashFlow

First off, thank you for considering contributing to FlashFlow! It's people like you that make FlashFlow such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by the [FlashFlow Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report for FlashFlow. Following these guidelines helps maintainers and the community understand your report, reproduce the behavior, and find related reports.

**Before Submitting A Bug Report**
- Check the [documentation](README.md) for tips on troubleshooting
- Determine which repository the bug should be reported in
- Check if the issue has already been reported

**How Do I Submit A (Good) Bug Report?**
Bugs are tracked as [GitHub issues](https://github.com/boifagusy/flashflow/issues). Create an issue and provide the following information:
- Use a clear and descriptive title
- Describe the exact steps which reproduce the problem
- Provide specific examples to demonstrate the steps
- Describe the behavior you observed after following the steps
- Explain which behavior you expected to see instead and why
- Include screenshots if possible
- Note the version of FlashFlow you're using

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for FlashFlow, including completely new features and minor improvements to existing functionality.

**Before Submitting An Enhancement Suggestion**
- Check if the enhancement has already been suggested
- Determine which repository the enhancement should be suggested in

**How Do I Submit A (Good) Enhancement Suggestion?**
Enhancement suggestions are tracked as [GitHub issues](https://github.com/boifagusy/flashflow/issues). Create an issue and provide the following information:
- Use a clear and descriptive title
- Provide a step-by-step description of the suggested enhancement
- Provide specific examples to demonstrate the steps
- Describe the current behavior and explain which behavior you expected to see instead
- Explain why this enhancement would be useful to most FlashFlow users

### Pull Requests

The process described here has several goals:
- Maintain FlashFlow's quality
- Fix problems that are important to users
- Engage the community in working toward the best possible FlashFlow
- Enable a sustainable system for FlashFlow's maintainers to review contributions

Please follow these steps to have your contribution considered by the maintainers:

1. Follow all instructions in [the template](.github/PULL_REQUEST_TEMPLATE.md)
2. Follow the [styleguides](#styleguides)
3. After you submit your pull request, verify that all [status checks](https://help.github.com/articles/about-status-checks/) are passing

While the prerequisites above must be satisfied prior to having your pull request reviewed, the reviewer(s) may ask you to complete additional design work, tests, or other changes before your pull request can be ultimately accepted.

## Styleguides

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line
- When only changing documentation, include `[ci skip]` in the commit title

### Python Styleguide

All Python code must adhere to [PEP 8](https://www.python.org/dev/peps/pep-0008/).

### Documentation Styleguide

- Use [Markdown](https://daringfireball.net/projects/markdown/) for documentation
- Reference methods and classes in markdown with backticks: `method_name`
- Reference issues and pull requests with pound signs: #123

## Additional Notes

### Issue and Pull Request Labels

This section lists the labels we use to help us track and manage issues and pull requests.

[GitHub search](https://help.github.com/articles/searching-issues/) makes it easy to use labels for finding groups of issues or pull requests you're interested in.

#### Type of Issue and Issue State

- `bug` - Issues that present incorrect or unexpected behavior
- `documentation` - Issues related to documentation
- `duplicate` - Issues that are duplicates of other issues
- `enhancement` - Issues that request new features
- `good first issue` - Issues that are good for new contributors
- `help wanted` - Issues that need assistance
- `invalid` - Issues that are invalid
- `question` - Issues that are questions
- `wontfix` - Issues that will not be fixed

#### Pull Request Labels

- `work in progress` - Pull requests that are not yet ready for review
- `needs review` - Pull requests that need reviewer attention
- `needs testing` - Pull requests that need manual testing

## Getting Started

For more information on setting up a development environment and running tests, see the [Developer Guide](FLASHFLOW_DEVELOPER_GUIDE.md).