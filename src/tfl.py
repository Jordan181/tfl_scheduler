import requests

def get_disruption_info(lines: str):
    url = f"https://api.tfl.gov.uk/Line/{lines}/Disruption"

    response = requests.get(url)

    if not response.ok:
        raise requests.HTTPError(response.content)
    
    json = response.json()
    return str(json)