#!/usr/bin/env python3
"""Simple mock client to exercise the CatCam backend HTTP endpoints.

Usage examples:
  python externalServer/scripts/mock_client.py init_db
  python externalServer/scripts/mock_client.py insert --filename test_cat.jpg
  python externalServer/scripts/mock_client.py classify_all
  python externalServer/scripts/mock_client.py images
  python externalServer/scripts/mock_client.py classify_image --id 1

The script defaults to http://localhost:8000 but you can set --base to another host.
"""
import argparse
import sys
import requests


def init_db(base):
    r = requests.post(f"{base}/init_db")
    print(r.status_code, r.text)


def insert_metadata(base, filename):
    payload = {"filename": filename}
    r = requests.post(f"{base}/insert_metadata", json=payload)
    print(r.status_code, r.json())


def classify_all(base):
    r = requests.post(f"{base}/classify_all")
    print(r.status_code, r.json())


def classify_image(base, image_id):
    r = requests.post(f"{base}/classify_image", json={"image_id": image_id})
    print(r.status_code, r.json())


def get_images(base, classified=None, cameraId=None, limit=None):
    params = {}
    if classified is not None:
        params['classified'] = classified
    if cameraId is not None:
        params['cameraId'] = cameraId
    if limit is not None:
        params['limit'] = limit
    r = requests.get(f"{base}/images", params=params)
    print(r.status_code, r.json())


def main():
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=['init_db', 'insert', 'classify_all', 'classify_image', 'images', 'delete', 'get'])
    p.add_argument('--base', default='http://localhost:8000', help='Base URL for the API')
    p.add_argument('--filename', help='Filename for insert')
    p.add_argument('--id', type=int, help='Image id for classify_image')
    p.add_argument('--classified', choices=['true','false'], help='Filter for images endpoint')
    p.add_argument('--cameraId', type=int, help='cameraId filter for images endpoint')
    p.add_argument('--limit', type=int, help='limit for images endpoint')
    args = p.parse_args()

    base = args.base.rstrip('/')

    try:
        if args.action == 'init_db':
            init_db(base)
        elif args.action == 'insert':
            if not args.filename:
                print('Please provide --filename for insert')
                sys.exit(2)
            insert_metadata(base, args.filename)
        elif args.action == 'classify_all':
            classify_all(base)
        elif args.action == 'classify_image':
            if not args.id:
                print('Please provide --id for classify_image')
                sys.exit(2)
            classify_image(base, args.id)
        elif args.action == 'images':
            classified = None
            if args.classified == 'true':
                classified = True
            elif args.classified == 'false':
                classified = False
            get_images(base, classified=classified, cameraId=args.cameraId, limit=args.limit)
        elif args.action == 'delete':
            if not args.id:
                print('Please provide --id for delete')
                sys.exit(2)
            # use HTTP DELETE
            r = requests.delete(f"{base}/images/{args.id}")
            print(r.status_code, r.text)
        elif args.action == 'get':
            if not args.id:
                print('Please provide --id for get')
                sys.exit(2)
            r = requests.get(f"{base}/images/{args.id}")
            print(r.status_code, r.json())
    except requests.ConnectionError as e:
        print('Failed to connect to', base, '-', e)
        sys.exit(1)


if __name__ == '__main__':
    main()
