# Script to start up webhook for SureBot

# Start Process Supervisor
supervisord -c supervisord.conf

python start_backend.py
