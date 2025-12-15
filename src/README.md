# FlashFlow Project Structure

This document describes the standardized folder structure for FlashFlow projects, following conventions similar to popular frameworks like Laravel and Flutter.

## Directory Structure

```
src/
├── flows/              # FlashFlow definition files (.flow)
├── models/             # Data models and database schemas
├── components/         # Reusable UI components
├── pages/              # Page definitions and layouts
├── services/           # Business logic and API integrations
├── utils/              # Utility functions and helpers
├── assets/             # Static assets (images, icons, fonts)
├── config/             # Configuration files
└── tests/              # Test files (.testflow and unit tests)
```

## Folder Descriptions

### flows/
Contains all FlashFlow definition files with `.flow` extension. These files define the structure and behavior of your application.

Example:
```
app.flow
user.flow
product.flow
```

### models/
Contains data model definitions that represent your application's data structures.

Example:
```
user.py
product.py
order.py
```

### components/
Contains reusable UI components that can be used across different pages.

Example:
```
button.py
card.py
form.py
```

### pages/
Contains page definitions and layouts for different sections of your application.

Example:
```
home.py
profile.py
dashboard.py
```

### services/
Contains business logic, API integrations, and service layer implementations.

Example:
```
auth_service.py
payment_service.py
email_service.py
```

### utils/
Contains utility functions and helper classes used throughout the application.

Example:
```
helpers.py
validators.py
formatters.py
```

### assets/
Contains static assets such as images, icons, and fonts.

Example:
```
images/
icons/
fonts/
```

### config/
Contains configuration files for different environments.

Example:
```
database.py
auth.py
api.py
```

### tests/
Contains test files including `.testflow` files and unit tests.

Example:
```
user.testflow
test_models.py
test_services.py
```

## Best Practices

1. **Organize by feature**: Group related files together when possible
2. **Use descriptive names**: Choose clear, descriptive names for files and directories
3. **Maintain consistency**: Follow the established structure and naming conventions
4. **Separate concerns**: Keep business logic, UI components, and data models in their respective directories
5. **Keep it flat**: Avoid deeply nested directory structures when possible

This structure makes it easier for developers to navigate the codebase and understand where to place new files.