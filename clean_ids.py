import re
import sys
import logging

log_file = logging.getLogger(__name__)
logging.basicConfig(filename = 'pipeline_autid.log', encoding = 'utf-8', filemode = 'w', level = logging.INFO, format = '%(message)s')


def check_id(id):
	if re.match(r"[A-Za-z0-9_0]{11}$", id):
		print(id, end="")
	else:
		log_file.info(id)

def main():
	if sys.stdin.isatty():
		while True:
			try:
				current_id = input()
				check_id(current_id)
				print()
			except KeyboardInterrupt:
				sys.exit(0)

	else:
		try:
			for current_id in sys.stdin:
				check_id(current_id)

		except KeyboardInterrupt:
			sys.exit(0)


if __name__=="__main__":
	main()
