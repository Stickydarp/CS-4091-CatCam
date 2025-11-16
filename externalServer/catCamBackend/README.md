# CatCam — externalServer backend

## Purpose
-------
This repository contains the external server backend for the CatCam project. The backend provides a small set of utilities and command handlers to manage image metadata, store image files, and run classification. It is intentionally minimal and script-driven so team members can integrate different piece.

## Quick start (developer local)
-----------------------------
1. Prepare host folders (no demo data will be added by this step):

```bash
python3 externalServer/scripts/setup_environment.py --prepare-host
```

This creates `~/catcam_data/images` and `~/catcam_data/metadata` for mounting into the container or for local development usage.

2. (Optional) Build Docker image:

```bash
python3 externalServer/scripts/setup_environment.py --build-image
```

3. Run CLI inside the container (example: init DB)

```bash
# initialize DB inside mounted metadata folder
docker run --rm -v ~/catcam_data/images:/catCamData/images -v ~/catcam_data/metadata:/catCamData/metadata catcam-external:latest python -m catCamBackend.main init_db
```

4. Add an image and insert metadata (host path)

```bash
# copy image to host images folder
cp some_photo.jpg ~/catcam_data/images/my_photo.jpg
# insert metadata via the container CLI
docker run --rm -v ~/catcam_data/images:/catCamData/images -v ~/catcam_data/metadata:/catCamData/metadata catcam-external:latest python -m catCamBackend.main insert_metadata --filename=my_photo.jpg
```

5. Classify images (run inside container or integrate your classifier):

```bash
# run the demo classifier (stub)
docker run --rm -v ~/catcam_data/images:/catCamData/images -v ~/catcam_data/metadata:/catCamData/metadata catcam-external:latest python -m catCamBackend.main classify_all
```

## Development container (recommended for local dev)
-----------------------------------------------
If you plan to iterate on the code or run many commands, it's more convenient to use a single persistent development container instead of creating a new container per command. This repository includes a minimal `docker-compose.yml` and a helper script `dev.sh` to make that easy.

1. Start the dev container (builds the image and mounts your source so edits are visible immediately):

```bash
./dev.sh up
```

2. Common helper commands (run inside the running container; no new containers are created):

```bash
./dev.sh shell         # open an interactive shell in the dev container
./dev.sh demo          # run the demo script (creates demo_data images and populates demo DB)
./dev.sh test          # run the test harness (uses tmp_test_catcam)
./dev.sh init_db       # initialize DB inside the mounted metadata folder
./dev.sh list          # list all metadata rows (prints via pprint)
./dev.sh insert <fn>   # insert metadata for an image already placed in ~/catcam_data/images
./dev.sh classify_all  # classify only images that are not yet classified
./dev.sh down          # stop and remove the dev container
```

Notes:
- `./dev.sh up` mounts `./externalServer` into `/app` inside the container so you can edit Python files on the host and run them immediately inside the container without rebuilding the image.
- Pillow is included in `externalServer/requirements.txt` so the demo image-generation works out of the box.
- If your system uses `docker-compose` (dash) instead of the `docker compose` plugin, either replace `docker compose` with `docker-compose` in `dev.sh` or run `docker-compose -f docker-compose.yml up -d` manually.

This workflow keeps a single container running for interactive development and demos while preserving the convenience of mounted host folders for images and metadata.

## Developer API (Python)
----------------------
If working inside the codebase, import the Python modules directly (this is what our demo scripts do):

```python
from catCamBackend import db_utils, commands
# initialize
db_utils.init_db()
# insert
commands.execute_command('insert_metadata', {'filename':'img.jpg', 'cameraId': 1, 'file_type':'jpg'})
# classify
commands.execute_command('classify_image', {'image_id': 1})
# query
commands.execute_command('get_images', {'classified': False, 'limit': 100})
```

## Demo scripts
------------
- `externalServer/scripts/setup_environment.py` — prepare host directories and optionally build docker image (no demo data is added when preparing host)
- `externalServer/scripts/demo_commands.py` — creates demo images locally inside `externalServer/demo_data`, populates and demonstrates insert/classify/query operations. Intended as an example run; does not write into the host `~/catcam_data` unless you choose to.

## Design notes / blueprint for future fields and queries
-----------------------------------------------------
- The DB schema contains: id, filename, timestamp, cameraId, file_type, classification, classified, confidence.
- `db_utils.query_images` supports querying on `classified` status, cameraId, timestamp ranges, and limit. Use this to export filtered datasets for a YOLO training pipeline.
- To export images + metadata for YOLO, call `query_images(classified=True)` and iterate returned metadata; image files live at `IMAGES_DIR + '/' + filename`.
