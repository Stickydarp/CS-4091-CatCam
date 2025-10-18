"""Small setup helper to create host data directories and optionally build the Docker image.

Usage:
  python3 externalServer/scripts/setup_environment.py --prepare-host
  python3 externalServer/scripts/setup_environment.py --build-image

--prepare-host: creates ~/catcam_data/images and ~/catcam_data/metadata (no demo data)
--build-image: runs docker build for externalServer (requires Docker)
"""
from pathlib import Path
import argparse
import subprocess
import sys

HOME = Path.home()
IMAGES = HOME / 'catcam_data' / 'images'
METADATA = HOME / 'catcam_data' / 'metadata'

parser = argparse.ArgumentParser()
parser.add_argument('--prepare-host', action='store_true', help='Create host folders for images and metadata')
parser.add_argument('--build-image', action='store_true', help='Build the docker image for externalServer')
args = parser.parse_args()

if args.prepare_host:
    IMAGES.mkdir(parents=True, exist_ok=True)
    METADATA.mkdir(parents=True, exist_ok=True)
    print('Created host folders:')
    print(' -', IMAGES)
    print(' -', METADATA)

if args.build_image:
    print('Building docker image catcam-external:latest from externalServer...')
    try:
        subprocess.check_call(['docker', 'build', '-t', 'catcam-external:latest', 'externalServer'], cwd=str(Path('.').resolve().parent))
    except FileNotFoundError:
        print('Docker not found. Please install Docker and try again.')
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print('Docker build failed with exit code', e.returncode)
        sys.exit(e.returncode)
    print('Docker image built')
