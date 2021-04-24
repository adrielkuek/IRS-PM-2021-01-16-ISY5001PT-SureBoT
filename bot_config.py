"""
General config file for Bot Server
"""

token = '<YOUR-BOT-TOKEN>'
telegram_base_url = 'https://api.telegram.org/bot{}/'
timeout = 100
model_download_url = '<MODEL-DOWNLOAD-URL>'
model_zip = 'pipeline_models.zip'
model_folder = '/pipeline_models'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_BROKER_URL = 'redis://localhost:6379/0'
