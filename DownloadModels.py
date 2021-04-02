import gdown
import zipfile, os

url = 'https://drive.google.com/uc?id=14cNpXSCiN0Wv1rcQYOjyzmty3RqOQYwC'
output = 'pipeline_models.zip'
gdown.download(url, output, quiet=False)

zip_ref = zipfile.ZipFile(output)  # createzipfileobject
zip_ref.extractall()  # extractfiletodir
zip_ref.close()  # closefile
os.remove(output)  # deletezippedfile
