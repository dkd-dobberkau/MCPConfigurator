# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The MCPConfigurator is a Python-based configuration management tool designed to:
- Combine individual JSON configuration files into a central JSON file
- Enable/disable specific configurations
- Manage configurations through a folder structure
- Create backups of configurations

The tool is implemented in a single file (`mcp_config_manager.py`) containing a `MCPConfigManager` class and a command-line interface.

## Commands

### Running the Tool

```bash
# View help and available commands
python mcp_config_manager.py --help

# Add a new configuration
python mcp_config_manager.py add path/to/config.json

# List available and active configurations
python mcp_config_manager.py list

# Enable a configuration
python mcp_config_manager.py enable config_name.json

# Disable a configuration
python mcp_config_manager.py disable config_name.json

# Combine active configurations
python mcp_config_manager.py combine

# Show combined configuration
python mcp_config_manager.py show

# Create a backup of combined configuration
python mcp_config_manager.py backup

# Specify a custom base directory
python mcp_config_manager.py --dir /custom/path command
```

## Project Structure

The tool organizes configurations in a directory structure:
- `mcp_configs/` - Base directory (default, can be customized)
  - `available/` - Stores all available configuration files
  - `active/` - Contains copies of active configurations
  - `backups/` - Stores backups of combined configurations
  - `claude_desktop_config.json` - The merged configuration file

## Code Architecture

The project is structured around a single `MCPConfigManager` class with methods for:
- Adding configurations (`add_config`)
- Enabling configurations (`enable_config`)
- Disabling configurations (`disable_config`)
- Listing configurations (`list_configs`)
- Creating backups (`create_backup`)
- Combining configurations (`combine_configs`)
- Showing the combined configuration (`show_combined_config`)

The command-line interface is implemented in the `main()` function using the `argparse` module.