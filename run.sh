#!/bin/bash

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
    echo "✅ Loaded environment variables from .env file"
else
    echo "⚠️  .env file not found, using default values"
fi

# Function to show usage
show_usage() {
    echo "Usage: $0 [dev|staging|prod|stop|down|logs]"
    echo ""
    echo "Commands:"
    echo "  dev      - Start development environment (default)"
    echo "  staging  - Start staging environment"
    echo "  prod     - Start production environment"
    echo "  stop     - Stop all services"
    echo "  down     - Stop and remove all containers"
    echo "  logs     - Show logs from all services"
    echo ""
    echo "Examples:"
    echo "  $0 dev     # Start development environment"
    echo "  $0 prod    # Start production environment"
    echo "  $0 logs    # Show logs"
    echo "  $0 down    # Stop and remove all containers"
}

# Default command
case "${1:-dev}" in
    "dev"|"")
        echo "🚀 Starting development environment..."
        docker-compose -f docker-compose.dev.yaml up --build
        ;;
    "stop")
        echo "⏹️  Stopping all services..."
        docker-compose -f docker-compose.dev.yaml down
        ;;
    "down")
        echo "🗑️  Stopping and removing all containers..."
        docker-compose -f docker-compose.dev.yaml down -v
        ;;
    "logs")
        echo "📋 Showing logs from all services..."
        docker-compose -f docker-compose.dev.yaml logs -f
        ;;
    "help"|"-h"|"--help")
        show_usage
        ;;
    *)
        echo "❌ Unknown command: $1"
        show_usage
        exit 1
        ;;
esac