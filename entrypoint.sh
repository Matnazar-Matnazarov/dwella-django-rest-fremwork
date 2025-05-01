#!/bin/bash

# Activate virtual environment (if it exists)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install dependencies
pip install -r requirements.txt

# Check for Redis service
if systemctl is-active --quiet redis-server; then
    echo "Redis server is already running"
else
    echo "Starting Redis server..."
    sudo systemctl enable redis-server
    sudo systemctl start redis-server
fi

# Apply database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start Django server in background
python manage.py runserver 0.0.0.0:8000 &
DJANGO_PID=$!

# Start Celery worker
celery -A config worker -l info &
CELERY_WORKER_PID=$!

# Start Celery beat
celery -A config beat -l info &
CELERY_BEAT_PID=$!


## doal boot
celery -A config.celery worker --beat --scheduler django --loglevel=info
 
# Function to handle termination
cleanup() {
    echo "Shutting down services..."
    kill $DJANGO_PID $CELERY_WORKER_PID $CELERY_BEAT_PID
    exit 0
}

# Register the cleanup function for when script receives SIGTERM
trap cleanup SIGINT SIGTERM

echo "Dwella is running!"
echo "Django server: http://127.0.0.1:8000"
echo "Admin panel: http://127.0.0.1:8000/secret/admin/"

# Keep script running
wait
