import requests
import json

class Clue():
	def __init__(self, offset=0, n_clues=100):
		self._base_url = f"http://cluebase.lukelav.in/clues?offset={offset}&limit={n_clues}"

	def _get_clues(self):
		request = requests.get(url=self._base_url)
		json_string = json.dumps(request.json(), indent=3)
		data = json.loads(json_string)
		return data


def main():
	asdf = Clue()
	print(asdf._get_clues())

if __name__ == "__main__":
	main()
