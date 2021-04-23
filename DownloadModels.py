import gdown
import zipfile, os
import config


url = config.model_download_url
output = config.model_zip
try:
    if os.path.isdir(os.path.dirname(os.path.realpath(__file__)) + config.model_folder):
        print("Required models are already available")
    else:
        gdown.download(url, output, quiet=False)
        zip_ref = zipfile.ZipFile(output)  # createzipfileobject
        zip_ref.extractall()  # extractfiletodir
        zip_ref.close()  # closefile
        os.remove(output)  # deletezippedfile
except:
    print("Models were not downloaded")
