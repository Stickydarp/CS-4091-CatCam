from pathlib import Path
import sys

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
EXTERNAL = ROOT / 'externalServer'
sys.path.insert(0, str(EXTERNAL))

from catCamBackend import db_utils, commands


def insert_three_images():
    # Ensure DB and directories exist
    db_utils.init_db()

    created = []
    inserted_ids = []
    for i in range(3):
        fname = f'kevin_demo_{i+1}.jpg'
        fpath = Path(db_utils.IMAGES_DIR) / fname
        # write a tiny JPEG-like header
        with open(fpath, 'wb') as f:
            f.write(b"\xff\xd8\xff\xdb\x00\x43\x00")
        print('Created image:', fpath)
        created.append(str(fpath))

        # Insert metadata and collect id
        image_id = db_utils.insert_metadata(filename=fname)
        print('Inserted metadata id:', image_id)
        inserted_ids.append(image_id)

    # Print the current images in DB
    all_meta = db_utils.get_all_metadata()
    print('\nCurrent metadata rows (most recent first):')
    for m in all_meta:
        print(m)

    return created, inserted_ids


if __name__ == '__main__':
    insert_three_images()
