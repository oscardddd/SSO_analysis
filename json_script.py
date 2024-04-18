import json

filename = 'labeled_user.json'

with open(filename, 'r') as f:
    data = json.load(f)


def extract_url(key):
    parts = key.split('!')
    url = parts[1].split('-')[0]
    return url

# Refactor the original dictionary
refactored_data = {extract_url(key): value for key, value in data.items()}

filename2 = 'websites.json'

with open(filename2, 'w') as f:
    json.dump(refactored_data, f, indent=4)

# Output the refactored dictionary
# print(json.dumps(refactored_data, indent=4))