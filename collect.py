#!/usr/bin/env python3
"""Fetch a JSON API and save it into the project's `data/` folder.

Default URL: Taichung stop-of-route API for operator 0401 (as provided).

Usage examples:
  python collect.py
  python collect.py --url "<url>" --out data/myfile.json
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

try:
	import requests
except Exception:
	print("The 'requests' package is required. Install with: pip install requests", file=sys.stderr)
	raise


DEFAULT_URL = (
	"https://ticp.motc.gov.tw/motcTicket/api/StopOfRoute/Taichung/Operator/0401?$format=json"
)


def fetch_json(url: str, retries: int = 3, backoff: float = 1.0):
	session = requests.Session()
	last_exc = None
	for attempt in range(1, retries + 1):
		try:
			resp = session.get(url, timeout=15)
			resp.raise_for_status()
			return resp.json()
		except Exception as e:
			last_exc = e
			wait = backoff * attempt
			print(f"Attempt {attempt} failed: {e}. Retrying in {wait:.1f}s...")
			time.sleep(wait)
	raise RuntimeError(f"Failed to fetch JSON after {retries} attempts") from last_exc


def save_json(obj, out_path: str):
	out_path = Path(out_path)
	out_path.parent.mkdir(parents=True, exist_ok=True)
	# Write atomically
	tmp = out_path.with_suffix(out_path.suffix + ".tmp")
	with tmp.open("w", encoding="utf-8") as f:
		json.dump(obj, f, ensure_ascii=False, indent=2)
	tmp.replace(out_path)
	print(f"Saved JSON to: {out_path}")


def build_default_out(url: str) -> str:
	# Try to create a sane filename from the URL
	name = "taichung_stop_of_route_0401.json"
	return os.path.join("data", name)


# Map of common operator numbers to names; used by --all mode to build filenames
OPERATOR_MAP = {
	"0401": "中台灣客運",
	"0402": "中鹿客運",
	"0501": "台中客運",
	"0504": "巨業交通",
	"0602": "全航客運",
	"0801": "和欣客運",
	"0804": "東南客運",
	"0808": "臺中客運",
	"0906": "建明客運",
	"0911": "苗栗客運",
	"1101": "國光客運",
}


def sanitize_filename(name: str) -> str:
	"""Return a safe filename segment keeping Unicode (e.g. Chinese) but removing characters
	that are invalid in filenames. Replace spaces with underscores.
	"""
	invalid = '<>:"/\\|?*\n\r\t'
	cleaned = ''.join(ch for ch in name if ch not in invalid)
	cleaned = cleaned.replace(' ', '_')
	return cleaned.strip()


def main():
	parser = argparse.ArgumentParser(description="Fetch JSON from an API and save to data/ folder")
	parser.add_argument("--url", "-u", default=DEFAULT_URL, help="API URL to fetch")
	parser.add_argument("--out", "-o", default=None, help="Output file path (default: data/taichung_stop_of_route_0401.json)")
	parser.add_argument("--all", action="store_true", help="Fetch JSON for all operators defined in OPERATOR_MAP")
	parser.add_argument("--delay", type=float, default=1.0, help="Delay in seconds between requests when using --all")
	parser.add_argument("--retries", "-r", type=int, default=3, help="Number of retries on failure")
	args = parser.parse_args()

	if args.all:
		# When --all is used, iterate OPERATOR_MAP and fetch per-operator files.
		base_template = args.url
		# ensure the url contains 'Operator/' so we can replace the operator portion
		if "Operator/" not in base_template:
			print("The provided URL doesn't look like the expected template containing 'Operator/'.", file=sys.stderr)
			sys.exit(2)

		for op_code, op_name in OPERATOR_MAP.items():
			url = base_template.replace("Operator/0401", f"Operator/{op_code}")
			# filename format: route{code}_{OperatorName}.json (e.g. route0401_中台灣客運.json)
			out_path = os.path.join("data", f"route{op_code}_{sanitize_filename(op_name)}.json")
			print(f"Fetching operator {op_code} ({op_name}) -> {out_path}")
			try:
				data = fetch_json(url, retries=args.retries)
			except Exception as e:
				print(f"Failed to fetch {op_code}: {e}", file=sys.stderr)
				continue
			try:
				save_json(data, out_path)
			except Exception as e:
				print(f"Failed to save {out_path}: {e}", file=sys.stderr)
				continue
			time.sleep(args.delay)
		return

	out = args.out or build_default_out(args.url)

	try:
		data = fetch_json(args.url, retries=args.retries)
	except Exception as e:
		print(f"Error fetching JSON: {e}", file=sys.stderr)
		sys.exit(2)

	try:
		save_json(data, out)
	except Exception as e:
		print(f"Error saving JSON: {e}", file=sys.stderr)
		sys.exit(3)


if __name__ == "__main__":
	main()

