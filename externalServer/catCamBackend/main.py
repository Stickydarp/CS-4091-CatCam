
"""Simple command-line entrypoint for catCamBackend used in local testing.

This module can be executed with `python -m catCamBackend.main` and
accepts a few simple commands: init_db, insert_metadata, list, classify_all.
It intentionally does not require FastAPI.
"""

from argparse import ArgumentParser
from . import db_utils, commands


def main():
	parser = ArgumentParser()
	parser.add_argument('action', choices=['init_db','insert_metadata','list','classify_all','classify_image'])
	parser.add_argument('--filename')
	parser.add_argument('--image_id', type=int)
	args = parser.parse_args()

	if args.action == 'init_db':
		db_utils.init_db()
		print('db initialized at', db_utils.DB_FILE)
	elif args.action == 'insert_metadata':
		if not args.filename:
			print('filename required')
			return
		id = db_utils.insert_metadata(filename=args.filename)
		print('inserted', id)
	elif args.action == 'list':
		from pprint import pprint
		pprint(db_utils.get_all_metadata())
	elif args.action == 'classify_all':
		print("results =", commands.execute_command('classify_all'))
	elif args.action == 'classify_image':
		if not args.image_id:
			print('image_id required')
			return
		print("results =", commands.execute_command('classify_image', {'image_id': args.image_id}))


if __name__ == '__main__':
	main()
