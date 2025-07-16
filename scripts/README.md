# GitRot Docker Scripts

This folder contains helper scripts to simplify Docker operations for the GitRot project.

## Files

- **`docker-helper.sh`** - Main helper script with Docker Compose commands
- **`setup.sh`** - Quick setup script to configure aliases

## Quick Start

1. **Run the setup script:**

   ```bash
   ./scripts/setup.sh
   ```

2. **Use the helper script directly:**

   ```bash
   ./scripts/docker-helper.sh up
   ```

3. **Or use the alias (after setup):**
   ```bash
   gitrot up
   ```

## Available Commands

| Command                  | Description                            |
| ------------------------ | -------------------------------------- |
| `up`                     | Build and start all services           |
| `down`                   | Stop and remove all services           |
| `start`                  | Start services (without building)      |
| `stop`                   | Stop services                          |
| `restart`                | Restart services                       |
| `build`                  | Build all services                     |
| `status`                 | Show service status and URLs           |
| `logs [service]`         | Show logs (all or specific service)    |
| `tail [lines] [service]` | Show recent logs                       |
| `exec <service> <cmd>`   | Execute command in container           |
| `shell [service]`        | Open shell in container                |
| `health`                 | Check service health                   |
| `clean`                  | Remove all containers, images, volumes |
| `help`                   | Show help message                      |

## Examples

```bash
# Start the entire application
gitrot up

# View logs for all services
gitrot logs

# View only backend logs
gitrot logs backend

# Open shell in backend container
gitrot shell backend

# Check if services are healthy
gitrot health

# Stop everything
gitrot down

# Clean up all Docker resources
gitrot clean
```

## Service URLs

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **Backend Health:** http://localhost:8000/health

## Features

- ✅ Colored output for better readability
- ✅ Error handling and validation
- ✅ Health checks for services
- ✅ Easy log viewing with filtering
- ✅ Container shell access
- ✅ Complete cleanup functionality
- ✅ Service status monitoring
- ✅ Dependency checking (Docker/Docker Compose)

## Notes

- The script automatically changes to the project root directory
- All Docker Compose commands are executed from the correct context
- The script includes safety prompts for destructive operations
- Health checks verify both backend API and frontend accessibility
