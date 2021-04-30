"""
Utility script to download and unzip models to the relevant folder
"""

import gdown
import zipfile, os
import bot_config


url = '<MODEL-DOWNLOAD-URL>'
output = bot_config.model_zip
try:
    if os.path.isdir(os.path.dirname(os.path.realpath(__file__)) + bot_config.model_folder):
        print("Required models are already available")
    else:
        gdown.download(url, output, quiet=False)
        zip_ref = zipfile.ZipFile(output)  # createzipfileobject
        zip_ref.extractall()  # extractfiletodir
        zip_ref.close()  # closefile
        os.remove(output)  # deletezippedfile
except:
    print("Models were not downloaded")
