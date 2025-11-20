"""Demo script for group members showing how to use the backend commands.

This script will:
- create a temporary demo folder under externalServer/demo_data
- create three simple images (red, green, blue boxes)
- init the database in the demo metadata folder
- insert metadata for the images
- run classify_all
- demonstrate get_images and get_image

Run from repo root with:
  python3 externalServer/scripts/demo_commands.py
"""

from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
EXTERNAL = ROOT / 'externalServer'
DEMO = EXTERNAL / 'demo_data'

sys.path.insert(0, str(EXTERNAL))
from catCamBackend import db_utils, commands



def make_demo_images():
    if DEMO.exists():
        shutil.rmtree(DEMO)
    imgs = DEMO / 'images'
    meta = DEMO / 'metadata'
    imgs.mkdir(parents=True)
    meta.mkdir(parents=True)

    # create three colored boxes
    try:
        from PIL import Image
    except Exception:
        raise SystemExit('Please install Pillow to run the demo: pip install Pillow')

    colors = {'red':(255,0,0), 'green':(0,255,0), 'blue':(0,0,255)}
    for name, col in colors.items():
        img = Image.new('RGB', (128,128), color=col)
        path = imgs / f'{name}_box.jpg'
        img.save(path)
    return imgs, meta


def run_demo():
    imgs, meta = make_demo_images()

    # patch db paths for local demo
    db_utils.DB_FILE = str((meta / 'db.sqlite3').resolve())
    db_utils.IMAGES_DIR = str(imgs.resolve())

    print('DB_FILE ->', db_utils.DB_FILE)
    print('IMAGES_DIR ->', db_utils.IMAGES_DIR)

    db_utils.init_db()
    print('DB initialized')

    # show DB before inserts
    print('\nDB before inserts:')
    print(db_utils.get_all_metadata())

    # insert images via commands.execute_command to show the command flow (explicit)
    ids = []
    print('\nInserting metadata for blue_box.jpg')
    res = commands.execute_command('insert_metadata', {
        'filename': 'blue_box.jpg',
        'cameraId': 1,
        'file_type': 'jpg',
        'classification': None,
        'classified': False,
        'confidence': None
    })
    print('insert_metadata response:', res)
    if isinstance(res, dict) and 'id' in res:
        ids.append(res['id'])
        print('Inserted metadata record:', commands.execute_command('get_image', {'image_id': res['id']}))

    print('\nInserting metadata for green_box.jpg')
    res = commands.execute_command('insert_metadata', {
        'filename': 'green_box.jpg',
        'cameraId': 2,
        'file_type': 'jpg',
        'classification': None,
        'classified': False,
        'confidence': None
    })
    print('insert_metadata response:', res)
    if isinstance(res, dict) and 'id' in res:
        ids.append(res['id'])
        print('Inserted metadata record:', commands.execute_command('get_image', {'image_id': res['id']}))

    print('\nInserting metadata for red_box.jpg')
    res = commands.execute_command('insert_metadata', {
        'filename': 'red_box.jpg',
        'cameraId': 3,
        'file_type': 'jpg',
        'classification': None,
        'classified': False,
        'confidence': None
    })
    print('insert_metadata response:', res)
    if isinstance(res, dict) and 'id' in res:
        ids.append(res['id'])
        print('Inserted metadata record:', commands.execute_command('get_image', {'image_id': res['id']}))

    print('\nRunning classify_all')
    print(commands.execute_command('classify_all'))

    print('\nAll images (get_images)')
    print(commands.execute_command('get_images', {'limit': 10}))

    print('\nGet single image (get_image)')
    print(commands.execute_command('get_image', {'image_id': ids[0]}))

if __name__ == '__main__':
    run_demo()
