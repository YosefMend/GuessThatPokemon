import requests
from bs4 import BeautifulSoup
from pathlib import Path
import csv
import re

def fix_name_spacing(name: str):
    # Function to add a space between lowercase-uppercase letter transitions. i.e. RattataAlolan Form --> Rattata Alolan Form
    return re.sub(r'([a-z])([A-Z])', r'\1 \2', name)

def extract_pokemon_names(url: str, output_folder):
    # Fetch and parse the webpage
    response = requests.get(url)
    print(f"HTTP Response Status: {response.status_code}")

    if response.status_code == 200:
        print("Page fetched successfully.")
        soup = BeautifulSoup(response.content, 'html.parser')
        print("Soup created successfully.")

        # Define the folder and ensure it exists
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True) # Ensure the folder exists
        csv_path = output_path / "pokemon_names.csv"

        # Locate the specific tables, all pokemon-related tables in bulbapedia have an attribute class: roundy
        tables = soup.find_all('table', {'class': 'roundy'})
        pokemon_names = []
        # Checking tables output
        # print("***********************************", tables[0].prettify(), "****************************************")

        # Loop through each table
        for table in tables:
            tbody = table.find('tbody')  # Find the tbody element inside the table
            if tbody:
                rows = tbody.find_all('tr')  # Get all rows in the tbody
                i = 0  # Counter for rows

                while i < len(rows):
                    row = rows[i]
                    # Checking rows output
                    # print("************************************", row.prettify(), "********************************")
                    cells = row.find_all('td')  # Get all cells (columns) in the row

                    if len(cells) > 1 and 'rowspan' in cells[0].attrs:
                        # If the first <td> has a rowspan, determine how many rows to process
                        rowspan = int(cells[0].attrs['rowspan'])  # Get rowspan value

                        # Process the first row (use third <td> index 2)
                        name = fix_name_spacing(cells[2].get_text(strip=True))
                        pokemon_names.append(name)
                        print(f"Extracted: {name}")
                        i += 1  # Move to the next row

                        # Process the following rows (use second <td> index 1)
                        for _ in range(1, rowspan):
                            if i < len(rows):
                                row = rows[i]
                                cells = row.find_all('td')
                                if len(cells) > 1:
                                    name = fix_name_spacing(cells[1].get_text(strip=True))
                                    pokemon_names.append(name)
                                    print(f"Extracted: {name}")
                                i += 1  # Move to the next row
                    elif len(cells) > 2:
                        # Handle normal rows (rowspan = 1)
                        name = fix_name_spacing(cells[2].get_text(strip=True))
                        pokemon_names.append(name)
                        print(f"Extracted: {name}")
                        i += 1
                    else:
                        i += 1

        pokemon_names = [fix_name_spacing(name) for name in pokemon_names]


        with csv_path.open(mode="w", newline="") as file:
            writer = csv.writer(file)
            for name in pokemon_names:
                writer.writerow([name])

        print(f"Saved {len(pokemon_names)} Pokemon names to '{csv_path}'.")
        return pokemon_names
    else:
        print(f"Failed to fetch URL. Status Code: {response.status_code}")
        return []
