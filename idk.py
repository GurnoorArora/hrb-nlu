import tarfile

tar_path = "C:/Users/X2832629/Downloads/en_core_web_sm-3.7.1.tar.gz"
extract_to = "C:/Users/X2832629/Downloads/en_model_extracted"

with tarfile.open(tar_path, "r:gz") as tar:
    tar.extractall(path=extract_to)
