#!/bin/sh

# Create the target directory if it doesn't exist
mkdir -p /chroma_db
mkdir -p /container_marker  # Create a directory for container-specific markers

# Check if chroma_db is empty
if [ -z "$(ls -A /chroma_db)" ]; then
    echo "Initializing database"
    cp -r /hb_agent/Data* /chroma_db/
    touch /container_marker/initialized_marker  # Create a marker file in the container-specific directory 
else
    echo "Database already initialized"
fi

exec uvicorn main:app --host 0.0.0.0 --port 5000