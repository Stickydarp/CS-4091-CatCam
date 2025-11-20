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
import os

SCRIPT_PATH = Path(__file__).resolve()   # full path to this script
SCRIPT_DIR = SCRIPT_PATH.parent          # externalServer/scripts
PROJECT_ROOT = SCRIPT_DIR.parent.parent  # CS-4091-CatCam
IMAGES = PROJECT_ROOT / 'catcam_data' / 'images'
METADATA = PROJECT_ROOT / 'catcam_data' / 'metadata'

parser = argparse.ArgumentParser()
parser.add_argument('--prepare-host', action='store_true', help='Create host folders for images and metadata')
parser.add_argument('--build-image', action='store_true', help='Build the docker image for externalServer')
args = parser.parse_args()

if args.prepare_host:
    IMAGES.mkdir(parents=True, exist_ok=True)
    METADATA.mkdir(parents=True, exist_ok=True)

    # Try to set permissive ownership and permissions so tools run as the current user
    uid = os.getuid()
    gid = os.getgid()
    try:
        # chown will silently fail if not permitted; that's acceptable
        os.chown(IMAGES, uid, gid)
        os.chown(METADATA, uid, gid)
    except PermissionError:
        pass
    try:
        os.chmod(IMAGES, 0o775)
        os.chmod(METADATA, 0o775)
    except PermissionError:
        pass

    print('Created host folders:')
    print(' -', IMAGES)
    print(' -', METADATA)

    # Write a small .env file that can be sourced to set CATCAM_* variables for host runs
    env_file = PROJECT_ROOT / '.catcam_env'
    try:
        with open(env_file, 'w') as f:
            f.write(f"# Source this file to configure CATCAM paths for host-side scripts\n")
            f.write(f"export CATCAM_IMAGES_DIR=\"{IMAGES}\"\n")
            f.write(f"export CATCAM_METADATA_DIR=\"{METADATA}\"\n")
        try:
            os.chown(env_file, uid, gid)
        except PermissionError:
            pass
        print('Wrote helper env file:', env_file)
        print('You can run: source', env_file)
    except Exception as e:
        print('Could not write helper env file:', e)

if args.build_image:
    print('Building docker image catcam-external:latest from externalServer...')
    try:
        subprocess.check_call(['docker', 'build', '-t', 'catcam-external:latest', 'externalServer'], cwd=str(PROJECT_ROOT))
    except FileNotFoundError:
        print('Docker not found. Please install Docker and try again.')
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print('Docker build failed with exit code', e.returncode)
        print(IMAGES)
        print(METADATA)
        sys.exit(e.returncode)
    print('Docker image built')
