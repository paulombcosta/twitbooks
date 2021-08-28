import spacy
from twitbooks.console import download_progress
from urllib.request import urlopen
from functools import partial
from twitbooks.config import get_config_path
import tarfile
import os

BASE_URL = "https://github.com/explosion/spacy-models/releases/download/{model}/{model}.tar.gz"

MODEL_VERSION = "3.1.0"


def new(lang: str, size: str):
    config_path = get_config_path()
    version_path = f"{lang}_core_web_{size}-{MODEL_VERSION}"
    model_name_path = f"{lang}_core_web_{size}"
    model_path = config_path.joinpath(version_path, model_name_path, version_path)
    nlp = spacy.load(model_path)
    return NER(nlp)


def download_and_extract_model(lang: str, size: str):
    model = "{}_core_web_{}-{}".format(lang, size, MODEL_VERSION)
    _download_model(model)
    _extract_model(model)


def is_model_downloaded(lang: str, size: str) -> bool:
    model_root = get_config_path().joinpath(f"{lang}_core_web_{size}-{MODEL_VERSION}")
    return model_root.is_dir()


def _download_model(model):
    progress = download_progress()
    progress.console.log(f"Downloading model")
    task = progress.add_task("download", filename=model, start=False)
    output = get_config_path().joinpath(f"{model}.tar.gz")
    with progress:
        response = urlopen(BASE_URL.format(model=model))
        progress.update(task, total=int(response.info()["Content-length"]))
        with output.open("wb") as dest_file:
            progress.start_task(task)
            for data in iter(partial(response.read, 32768), b""):
                dest_file.write(data)
                progress.update(task, advance=len(data))
    progress.console.log(f"Downloaded {model}")


def _extract_model(model):
    tar_file = get_config_path().joinpath(f"{model}.tar.gz")
    tar = tarfile.open(tar_file, "r:gz")
    tar.extractall(path=get_config_path())
    tar.close()
    os.remove(tar_file)


class NER:
    def __init__(self, nlp):
        self.nlp = nlp

    def process(self, text: str):
        doc = self.nlp(text)
        ents = [e.text for e in doc.ents if e.label_ == 'WORK_OF_ART']
        return ents
