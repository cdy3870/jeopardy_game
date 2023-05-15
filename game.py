import requests
import json

class Game():
	def __init__(self, ids):
		self.ids = ids

	def _get_game(self, url):
		request = requests.get(url=url)
		json_string = json.dumps(request.json(), indent=3)
		data = json.loads(json_string)
		return data

	def _get_games_from_ids(self):
		data_list = []
		for id in self.ids:
			url = f"http://cluebase.lukelav.in/games/{id}"
			data_list.append(self._get_game(url)["data"][0])

		# print(data_list)

		return data_list



def main():
	asdf = Game([1, 2, 5])
	print(asdf._get_games_from_ids())

if __name__ == "__main__":
	main()
