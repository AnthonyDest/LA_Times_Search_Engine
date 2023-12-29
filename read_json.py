## NOT TO BE USED, FOR VIEWING PURPOSES ONLY
import json

def count_elements(json_data):
    total_elements = 0

    for row in json_data:
        if isinstance(row, list):
            total_elements += len(row)
            for item in row:
                if isinstance(item, dict):
                    total_elements += len(item)
        elif isinstance(row, dict):
            total_elements += len(row)

    return total_elements

# Read the JSON file
with open('./OutputFolder/inverted_index.json', 'r') as file:
    json_data = json.load(file)

# Count the total number of elements
total_elements = count_elements(json_data)

print(f'Total number of elements: {total_elements}')
