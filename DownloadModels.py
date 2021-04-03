import gdown
import zipfile, os


url = 'https://drive.google.com/uc?id=14cNpXSCiN0Wv1rcQYOjyzmty3RqOQYwC'
output = 'pipeline_models.zip'
try:
    if os.path.isdir(os.path.dirname(os.path.realpath(__file__)) + '/pipeline_models'):
        print("Required models are already available")
    else:
        gdown.download(url, output, quiet=False)
        zip_ref = zipfile.ZipFile(output)  # createzipfileobject
        zip_ref.extractall()  # extractfiletodir
        zip_ref.close()  # closefile
        os.remove(output)  # deletezippedfile
except:
    print("Models were not downloaded")
