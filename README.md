# Qubership Envgene Template

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Templates for creating Qubership Envgene instances with support for various environments and configurations.

## Description

This repository contains a Maven artifact with templates for deploying and configuring Qubership Envgene instances. The templates support various environments (dev, svt) and include configurations for cloud infrastructure, ArgoCD, BSS, and other components.

## Project Structure

```
qubership-envgene-template/
├── templates/                          # Main templates
│   ├── env_templates/                  # Environment templates
│   │   ├── dev/                        # Development environment
│   │   │   ├── cloud.yml.j2           # Cloud configuration
│   │   │   ├── tenant.yml.j2          # Tenant configuration
│   │   │   └── Namespaces/            # Namespaces
│   │   │       ├── core.yml.j2        # Core components
│   │   │       ├── bss.yml.j2         # BSS components
│   │   │       ├── data-management.yml.j2
│   │   │       ├── data-migration.yml.j2
│   │   │       └── datahub.yml.j2
│   │   ├── dev.yaml                    # Dev environment configuration
│   │   └── svt.yaml                    # SVT environment configuration
│   ├── parameters/                      # Configuration parameters
│   │   ├── argocd-configuration/       # ArgoCD configuration
│   │   ├── bss-configuration/          # BSS configuration
│   │   ├── ci-configuration/           # CI/CD configuration
│   │   ├── cloud-configuration/        # Cloud configuration
│   │   ├── env-specific-configuration/ # Environment-specific settings
│   │   └── wa/                         # Workaround configurations
│   └── resource_profiles/               # Resource profiles
│       ├── dev_bss.yml                 # BSS resource profile for dev
│       ├── dev_core.yml                # Core resource profile for dev
│       ├── svt_bss.yml                 # BSS resource profile for SVT
│       └── svt_core.yml                # Core resource profile for SVT
├── src/assembly/                        # Maven assembly configuration
├── pom.xml                             # Maven configuration
└── README.md                           # Documentation
```

## Features

### 🚀 Supported Environments
- **Development (dev)** - development environment
- **SVT (Software Verification Testing)** - testing environment

### ☁️ Cloud Infrastructure
- Cloud resource configuration
- PostgreSQL database support
- Parallel execution settings

### 🔄 CI/CD Integration
- ArgoCD configuration for GitOps
- CI/CD pipeline settings
- E2E testing

### 🏗️ System Components
- **Core** - core system components
- **BSS (Business Support System)** - business support system
- **Data Management** - data management
- **Data Migration** - data migration
- **DataHub** - data hub

### 📊 Resource Profiles
- CPU and memory settings for various components
- Base profiles for different environments
- Flexible resource configuration

## Installation

### Requirements
- Java 8+
- Maven 3.6+
- Docker (optional)

### Building from Source

```bash
git clone https://github.com/Netcracker/qubership-envgene-template.git
cd qubership-envgene-template
mvn clean package
```

### Using Maven Artifact

```xml
<dependency>
    <groupId>org.qubership</groupId>
    <artifactId>qubership_envgene_templates</artifactId>
    <version>0.0.10</version>
    <type>zip</type>
</dependency>
```

## Usage

### 1. Environment Selection

Choose the appropriate environment template:

- **dev.yaml** - for development
- **svt.yaml** - for testing

### 2. Parameter Configuration

Configure parameters in the corresponding configuration files:

- `cloud-configuration.yml` - cloud settings
- `argocd-configuration.yml` - ArgoCD settings
- `bss-configuration/` - BSS settings

### 3. Applying Templates

Use the selected templates for deployment:

```bash
# Example of applying dev environment
envgene apply -f templates/env_templates/dev.yaml

# Example of applying SVT environment
envgene apply -f templates/env_templates/svt.yaml
```

## Configuration

### Cloud Settings

```yaml
version: 23.3
name: cloud-configuration
parameters:
    ESCAPE_SEQUENCE: "true"
    DISABLE_PARALLEL_EXECUTION: true
    RUN_PARALLEL_EXECUTION: false
    USE_POSTGRESQL_AS_DB: "true"
```

### ArgoCD Settings

```yaml
version: 24.1
name: argocd-configuration
parameters: 
  ARGOCD_URL: "https://argocd-server.${CLOUD_PUBLIC_HOST}"
  ARGOCD_MAX_RETRY: '250'
  ARGOCD_WAIT_TIMEOUT: '5'
  ARGOCD_FAST_FAIL: 'true'
```

### Resource Profiles

```yaml
name: "dev_core"
version: 1
baseline: "dev"
applications:
  - name: "Cloud-Core"
    services:     
      - name: "control-plane"
        parameters:
          - name: "CPU_REQUEST"
            value: "10m"
          - name: "MEMORY_REQUEST"
            value: "120Mi"
```

## Development

### Adding New Templates

1. Create a new template file in the appropriate directory
2. Update the environment configuration
3. Add necessary parameters
4. Test the template

### Adding New Environments

1. Create a new configuration file in `templates/env_templates/`
2. Define necessary templates and overrides
3. Create corresponding resource profiles
4. Update documentation

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Support

- **Developer**: Netcracker Technology
<!-- markdownlint-disable-next-line MD034 -->
- **Email**: opensourcegroup@netcracker.com.
- **GitHub**: https://github.com/Netcracker/qubership-envgene-template

## Contributing

We welcome contributions to the project! Please read our contributing guidelines.

## Versions

Current version: **0.0.1**

Full version history is available in [CHANGELOG.md](CHANGELOG.md) (if available).

---

**Note**: This project is part of the Qubership ecosystem and is intended for use in the Netcracker Technology corporate environment.