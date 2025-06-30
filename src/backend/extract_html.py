import requests
from bs4 import BeautifulSoup
import json

def parse_log_sections(url):
    response = requests.get(url)
    response.encoding = 'utf-8'
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    sections = soup.select('section[id] > section')  # Nested sections like ACC, ADSB
    log_entries = []

    for sec in sections:
        log_type = sec.find('h2').get_text(strip=True)[:-1]
        description = sec.find('p').get_text(strip=True)

        # Extract table rows
        table = sec.find('table')
        fields = []
        if table:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) == 3:
                    field_name = cols[0].get_text(strip=True)
                    unit = cols[1].get_text(strip=True)
                    meaning = cols[2].get_text(strip=True)
                    fields.append({
                        "name": field_name,
                        "unit": unit,
                        "meaning": meaning
                    })

        log_entries.append({
            "log_type": log_type,
            "description": description,
            "fields": fields
        })

    return log_entries


def main():
    url = "https://ardupilot.org/plane/docs/logmessages.html"
    data = parse_log_sections(url)

    # Preview first 2 log types
    for entry in data[:2]:
        print(f"\n📘 Log Type: {entry['log_type']}")
        print(f"📝 Description: {entry['description']}")
        for field in entry['fields']:
            print(f"  - {field['name']} ({field['unit']}): {field['meaning']}")

    # Optionally write to file
    with open("log_definitions.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
