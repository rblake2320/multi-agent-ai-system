# Multi-Agent AI System

Advanced Multi-Agent AI System with Hive Collective Intelligence - Complete End-to-End Solution

## Overview

This repository contains a sophisticated multi-agent AI system that leverages collective intelligence to build complete applications. The system features a four-zone architecture with specialized AI agents working together to deliver real, deployable code.

## Architecture

### Zone 1: Hive Collective Intelligence
- **5 Specialized Personas**: Architect, Innovator, Pragmatist, Quality Advocate, User Champion
- **Consensus Mechanism**: Structured debate and decision-making process
- **Strategic Planning**: High-level requirements analysis and architecture design

### Zone 2: Orchestration & Routing
- **Task Coordination**: Intelligent routing of tasks to specialized agents
- **Dependency Management**: Ensures proper sequencing of development tasks
- **Resource Optimization**: Efficient allocation of agent capabilities

### Zone 3: Execution Agents
- **Code Generation Agent**: Creates real, working code
- **Testing Agent**: Implements comprehensive test suites
- **DevOps Agent**: Handles deployment and infrastructure
- **Security Agent**: Ensures security best practices
- **Documentation Agent**: Creates comprehensive documentation

### Zone 4: Output Assembly & Validation
- **Quality Assurance**: Validates all generated components
- **Integration Testing**: Ensures components work together
- **Final Assembly**: Packages complete, deployable applications

## Features

- ✅ **Real Code Generation**: Produces actual, working applications
- ✅ **Multi-Agent Collaboration**: 5+ specialized AI agents working together
- ✅ **Quality Assurance**: Built-in testing and validation
- ✅ **Deployment Ready**: Generates Docker configurations and deployment scripts
- ✅ **Comprehensive Documentation**: Auto-generated docs and README files

## Technology Stack

### Backend
- **Framework**: FastAPI
- **Database**: SQLAlchemy with SQLite/PostgreSQL support
- **Authentication**: JWT-based authentication
- **Real-time**: WebSocket support
- **API**: RESTful API with OpenAPI documentation

### Frontend
- **Framework**: React with Vite
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui component library
- **State Management**: React hooks and context

### Infrastructure
- **Containerization**: Docker and Docker Compose
- **Deployment**: Production-ready configurations
- **Monitoring**: Built-in health checks and metrics
- **Testing**: Comprehensive test suites

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/rblake2320/multi-agent-ai-system.git
   cd multi-agent-ai-system
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start the system**
   ```bash
   python src/main.py
   ```

### Using the System

1. **Access the API**
   - Main API: `http://localhost:8001`
   - Documentation: `http://localhost:8001/docs`
   - Health Check: `http://localhost:8001/health`

2. **Create a project**
   ```bash
   curl -X POST http://localhost:8001/api/v1/projects/ \
     -H "Content-Type: application/json" \
     -d '{
       "name": "My Web App",
       "description": "A complete web application",
       "project_type": "web_application",
       "requirements": "user authentication, responsive design, database integration"
     }'
   ```

3. **Monitor progress**
   ```bash
   curl http://localhost:8001/api/v1/projects/{project_id}/status
   ```

4. **Get results**
   ```bash
   curl http://localhost:8001/api/v1/projects/{project_id}/results
   ```

## Project Structure

```
multi-agent-ai-system/
├── src/
│   ├── core/                    # Core system components
│   │   ├── database.py         # Database configuration
│   │   └── system_manager.py   # Main system orchestrator
│   ├── zone1_hive_collective/   # Hive Collective Intelligence
│   │   ├── personas/           # AI personas
│   │   ├── debate_engine/      # Debate coordination
│   │   └── consensus_builder/  # Consensus mechanisms
│   ├── zone2_orchestration/     # Task orchestration
│   ├── zone3_execution_agents/  # Specialized execution agents
│   ├── zone4_output_assembly/   # Output assembly and validation
│   ├── api/                    # REST API endpoints
│   ├── utils/                  # Utility functions
│   └── main.py                 # Application entry point
├── config/                     # Configuration files
├── tests/                      # Test suites
├── docs/                       # Documentation
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## API Documentation

### Core Endpoints

- `GET /health` - System health check
- `GET /api/v1/projects/` - List all projects
- `POST /api/v1/projects/` - Create new project
- `GET /api/v1/projects/{id}/status` - Get project status
- `GET /api/v1/projects/{id}/results` - Get project results

### Project Types Supported

- **Web Applications**: Full-stack web apps with frontend and backend
- **APIs**: RESTful APIs with documentation
- **Chat Applications**: Real-time chat with WebSocket support
- **E-commerce**: Complete e-commerce platforms
- **Dashboards**: Data visualization and analytics dashboards

## Testing

Run the comprehensive test suite:

```bash
python test_system.py
```

This will test:
- ✅ System health and status
- ✅ Project creation and processing
- ✅ Multi-agent coordination
- ✅ Code generation quality
- ✅ Integration workflows

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
- Create an issue in this repository
- Contact: rblake2320@aol.com

## Roadmap

### Current Status
- ✅ Multi-agent system architecture
- ✅ Basic code generation
- ✅ API endpoints and documentation
- ✅ Database models and operations

### In Progress
- 🔄 Complete file generation (fixing missing components)
- 🔄 Frontend-backend integration
- 🔄 Enhanced quality validation
- 🔄 Deployment automation

### Planned Features
- 📋 Advanced project templates
- 📋 Cloud deployment integration
- 📋 Real-time collaboration features
- 📋 Advanced AI model integration
- 📋 Plugin system for custom agents

---

**Built with ❤️ by the Multi-Agent AI Team**

