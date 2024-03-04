"""new_dataset dataset."""

import tensorflow_datasets as tfds
from pathlib import Path




class JWSign(tfds.core.GeneratorBasedBuilder):
  """DatasetBuilder for new_dataset dataset."""

  VERSION = tfds.core.Version('1.0.0')
  RELEASE_NOTES = {
      '1.0.0': 'Initial release.',
  }
  _DESCRIPTION= """Jehovah Witness Sign Language: Parallel Corpus of Sign Language Video and Text Translation based on JW Bible Verses"""
  # newindex.list.gz
  # "https://drive.google.com/file/d/1LhyPOH6JrqmSYagL4SVHLW6SjwBhsnkf/view?usp=drive_link"
  _INDEX_URL="https://drive.google.com/uc?id=1LhyPOH6JrqmSYagL4SVHLW6SjwBhsnkf"
      
  # text51.dict.gz is at https://drive.google.com/file/d/1j6_AJODqlOnC3d5SfZp_y4AhjjegwjBX/view?usp=drive_link
  # split it up into individual JSONs, uploaded to https://drive.google.com/drive/folders/1r-ftcljPRm1kLasqCK_cYL9zc4mxE6_o
  # the JSON with the download links for each of them is spoken_lang_text_file_download_urls.json
  
  _SPOKEN_LANG_TEXT_FILE_DOWNLOAD_URLS_JSON = Path(__file__).parent.resolve() / "data"/ "spoken_lang_text_file_download_urls.json"

  def _info(self) -> tfds.core.DatasetInfo:
    """Returns the dataset metadata."""

    features = {
            # "id": tfds.features.Text(),
            # "signer": tfds.features.Text(),
            # "gloss": tfds.features.Text(),
            "text": tfds.features.Text(),
        }

    return tfds.core.DatasetInfo(
            builder=self,
            description=self._DESCRIPTION,
            features=tfds.features.FeaturesDict(features),
            # homepage=_HOMEPAGE,
            supervised_keys=None,
            # citation=_CITATION,
        )

  def _split_generators(self, dl_manager: tfds.download.DownloadManager):
    """Returns SplitGenerators."""
    # TODO(new_dataset): Downloads the data and defines the splits

    text_download_resource = tfds.download.Resource(self._TEXT_URL, extract_method=tfds.download.ExtractMethod.GZIP)
    path = dl_manager.download_and_extract(self._TEXT_URL)

    # TODO(new_dataset): Returns the Dict[split names, Iterator[Key, Example]]
    return {
        'train': self._generate_examples(path / 'train_imgs'),
    }

  def _generate_examples(self, path):
    """Yields examples."""
    # TODO(new_dataset): Yields (key, example) tuples from the dataset
    for f in path.glob('*.jpeg'):
      yield 'key', {
          'image': f,
          'label': 'yes',
      }
