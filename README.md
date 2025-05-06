# MCP Configuration Manager

A tool for managing, combining, and maintaining JSON configuration files for MCP systems.

## Features

- Add configuration files to a central repository
- Enable and disable specific configurations
- Combine active configurations into a single JSON file
- Create automatic backups of configurations
- Simple command-line interface

## Installation

No special installation required. Just make sure you have Python 3.6+ installed.

```bash
# Clone the repository (if applicable)
git clone https://github.com/dkd-dobberkau/MCPConfigurator.git
cd MCPConfigurator

# Make the script executable (Linux/Mac)
chmod +x mcp_config_manager.py
```

## Usage

```bash
# View help and available commands
python mcp_config_manager.py --help

# Add a new configuration file
python mcp_config_manager.py add path/to/config.json

# List available and active configurations
python mcp_config_manager.py list

# Enable a specific configuration
python mcp_config_manager.py enable config_name.json

# Disable a configuration
python mcp_config_manager.py disable config_name.json

# Combine all active configurations
python mcp_config_manager.py combine

# Show the current combined configuration
python mcp_config_manager.py show

# Create a backup manually
python mcp_config_manager.py backup

# Specify a custom base directory
python mcp_config_manager.py --dir /custom/path command
```

## Directory Structure

The tool creates and manages the following directory structure:

```
mcp_configs/          # Base directory (default location in current working directory)
├── available/        # All available configuration files
├── active/          # Active configuration files
├── backups/         # Backup files of combined configurations
└── claude_desktop_config.json  # The combined configuration file
```

You can specify a different base directory using the `--dir` option.

## How It Works

1. Configuration files are added to the `available` directory
2. Files are activated by copying them to the `active` directory
3. When combining, all active configurations are merged into a single JSON file
4. Backups are automatically created before each combination

When configurations have overlapping keys, the values from later files take precedence.

## Requirements

- Python 3.6+
- Standard library modules only (no external dependencies)

## Testing

The project includes unit tests to ensure functionality. Run the tests with:

```bash
# Run all unit tests
python test_mcp_config_manager.py
```

The test suite covers:
- Configuration initialization
- Adding valid and invalid configurations
- Enabling and disabling configurations
- Combining configurations (empty, single, and multiple)
- Deep merge functionality
- Backup creation
