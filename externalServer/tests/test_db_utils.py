import os
import importlib
from pathlib import Path


def setup_module(module):
    # ensure a clean env for tests
    pass


def test_db_init_and_crud(tmp_path, monkeypatch):
    # Point db modules to temp directories before import
    images_dir = tmp_path / "images"
    metadata_dir = tmp_path / "metadata"
    images_dir.mkdir()
    metadata_dir.mkdir()

    monkeypatch.setenv('CATCAM_IMAGES_DIR', str(images_dir))
    monkeypatch.setenv('CATCAM_METADATA_DIR', str(metadata_dir))

    # import db_utils after env set; /app is the externalServer folder in the container
    import catCamBackend.db_utils as db_utils
    importlib.reload(db_utils)

    # init and insert
    db_utils.init_db()
    image_id = db_utils.insert_metadata('sample.jpg')
    assert isinstance(image_id, int)

    all_meta = db_utils.get_all_metadata()
    assert len(all_meta) == 1
    meta = db_utils.get_metadata_by_id(image_id)
    assert meta['filename'] == 'sample.jpg'

    # update
    ok = db_utils.update_metadata(image_id, classification='cat', classified=True, confidence=0.9)
    assert ok
    meta2 = db_utils.get_metadata_by_id(image_id)
    assert meta2['classification'] == 'cat'
    assert meta2['classified'] is True

    # delete removes record
    ok = db_utils.delete_metadata(image_id)
    assert ok
    assert db_utils.get_metadata_by_id(image_id) is None
