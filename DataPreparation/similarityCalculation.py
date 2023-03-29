import requests
import json
class SimilarityCalculation:
    def compute_similarity(self, query, corpus):
        ENDPOINT = "http://127.0.0.1:9000/embed_cosine_multiple/"

        data = {"query": query, "corpus": corpus}
        headers = {'Content-type': 'application/json'}

        #https://stackoverflow.com/questions/9733638/how-to-post-json-data-with-python-requests
        r = requests.post(ENDPOINT, data = json.dumps(data), headers = headers)

        if r.status_code!=200:
            print("Error in data")
        else:
            print(f"Status Code: {r.status_code}, Response: {r.json()}")

        return r.json()["cos_scores"]