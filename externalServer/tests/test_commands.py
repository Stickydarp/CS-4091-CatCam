import os
import importlib
from pathlib import Path


def test_classify_all_with_stub(tmp_path, monkeypatch):
    images_dir = tmp_path / "images"
    metadata_dir = tmp_path / "metadata"
    images_dir.mkdir()
    metadata_dir.mkdir()

    monkeypatch.setenv('CATCAM_IMAGES_DIR', str(images_dir))
    monkeypatch.setenv('CATCAM_METADATA_DIR', str(metadata_dir))

    # Import modules after env is set; /app is the externalServer folder in the container
    import catCamBackend.db_utils as db_utils
    import catCamBackend.commands as commands
    importlib.reload(db_utils)
    importlib.reload(commands)

    # init and insert a file that exists
    db_utils.init_db()
    # create an actual image file so classifier can see it
    img_path = images_dir / 'maybe_cat.jpg'
    img_path.write_bytes(b'')

    image_id = db_utils.insert_metadata('maybe_cat.jpg')
    res = commands.classify_all()
    assert res['total entries'] == 1
    assert res['classified'] == 1 or res['unclassified'] == 0

    meta = db_utils.get_metadata_by_id(image_id)
    assert meta is not None
    assert meta['classified'] is True
