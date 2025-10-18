"""Test script for catCamBackend command handlers and Docker build.

This script will:
- create a temporary test data directory under ./tmp_test_catcam
- patch db_utils.DB_FILE and db_utils.IMAGES_DIR to point to that dir
- call init_db(), insert a metadata entry, create a dummy image file
- call execute_command for classify_image, classify_all, delete_image, clear_database
- attempt to build the Docker image for externalServer (if docker available)

Run from repository root as:
  python3 externalServer/scripts/test_commands.py
"""

import os
import shutil
import importlib
import sys
import subprocess
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[2]
EXTERNAL = ROOT / 'externalServer'
SCRIPTS = EXTERNAL / 'scripts'
TEST_DIR = EXTERNAL / 'tmp_test_catcam'

# Ensure module path
sys.path.insert(0, str(EXTERNAL))

# Import modules
import catCamBackend.db_utils as db_utils
import catCamBackend.commands as commands


def setup_test_dirs():
    if TEST_DIR.exists():
        shutil.rmtree(TEST_DIR)
    images_dir = TEST_DIR / 'images'
    metadata_dir = TEST_DIR / 'metadata'
    images_dir.mkdir(parents=True)
    metadata_dir.mkdir(parents=True)
    # Patch db paths
    db_utils.DB_FILE = str(metadata_dir / 'db.sqlite3')
    db_utils.IMAGES_DIR = str(images_dir)
    print('Patched DB_FILE ->', db_utils.DB_FILE)
    print('Patched IMAGES_DIR ->', db_utils.IMAGES_DIR)


def run_tests():
    # Init DB
    db_utils.init_db()
    print('DB initialized')

    # Create a dummy image file
    fname = 'test_cat_01.jpg'
    fpath = Path(db_utils.IMAGES_DIR) / fname
    with open(fpath, 'wb') as f:
        f.write(b'\xff\xd8\xff')  # write minimal bytes to represent a jpg header
    print('Dummy image created at', fpath)

    # Insert metadata
    image_id = db_utils.insert_metadata(filename=fname)
    print('Inserted metadata id', image_id)

    # Classify single image
    res = commands.execute_command('classify_image', {'image_id': image_id})
    print('classify_image result:', res)

    # Insert another file and classify all
    fname2 = 'random_file.png'
    fpath2 = Path(db_utils.IMAGES_DIR) / fname2
    with open(fpath2, 'wb') as f:
        f.write(b'PNG')
    id2 = db_utils.insert_metadata(filename=fname2)
    print('Inserted metadata id', id2)

    res_all = commands.execute_command('classify_all')
    print('classify_all result:', res_all)

    # Delete first image
    del_res = commands.execute_command('delete_image', {'image_id': image_id})
    print('delete_image result:', del_res)

    # Clear database
    clear_res = commands.execute_command('clear_database')
    print('clear_database result:', clear_res)


def try_docker_build():
    print('\nAttempting docker build for externalServer...')
    # Build image named catcam-external:test
    cmd = ['docker', 'build', '-t', 'catcam-external:test', '.']
    try:
        proc = subprocess.run(cmd, cwd=str(EXTERNAL), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=300)
        print('docker build exit', proc.returncode)
        print(proc.stdout[:4000])
    except FileNotFoundError:
        print('docker not found; skipping docker build')
    except subprocess.TimeoutExpired:
        print('docker build timed out; skipping')


if __name__ == '__main__':
    setup_test_dirs()
    run_tests()
    try_docker_build()
    print('\nTest run complete')
