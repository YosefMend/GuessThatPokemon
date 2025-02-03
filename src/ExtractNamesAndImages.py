import os
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import re


def download_image(img_url, save_path):
    """Download and save an image from a URL."""
    response = requests.get(img_url)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"Saved: {save_path}")
    else:
        print(f"Failed to download {img_url}")


def extract_pokemon_images(url: str, output_folder):
    """Extract Pokémon names and images, saving each image with its Pokémon name."""
    images_folder = Path(output_folder) / 'BulbapediaPokemonImages'
    images_folder.mkdir(parents=True, exist_ok=True)

    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch URL. Status Code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    print("Soup created successfully.")

    tables = soup.find_all('table', {'class': 'roundy'})
    pokemon_data = []

    for table in tables:
        tbody = table.find('tbody')
        if not tbody:
            continue

        rows = tbody.find_all('tr')
        i = 0

        while i < len(rows):
            row = rows[i]
            cells = row.find_all('td')

            if len(cells) > 1 and 'rowspan' in cells[0].attrs:
                rowspan = int(cells[0].attrs['rowspan'])

                # Extract primary Pokémon name
                img_tag = cells[1].find('img') if len(cells) > 1 else cells[0].find('img')
                pokemon_name = img_tag.get('alt', 'Unknown') if img_tag else 'Unknown'

                # Extract image URL
                if img_tag and 'src' in img_tag.attrs:
                    img_url = img_tag['src']
                    save_path = images_folder / f"{pokemon_name}.png"
                    download_image(img_url, save_path)
                    pokemon_data.append((pokemon_name, img_url))

                i += 1  # Move to next row

                # Process alternate forms
                for _ in range(1, rowspan):
                    if i < len(rows):
                        row = rows[i]
                        cells = row.find_all('td')

                        if len(cells) > 0:
                            img_tag = cells[0].find('img')

                            if img_tag and 'srcset' in img_tag.attrs:
                                # Extract name from srcset URL (last part of filename)
                                srcset_url = img_tag['srcset'].split()[-2]  # Last URL in srcset before descriptor
                                alt_name_match = re.search(r'(\d+)([A-Za-z\-]+)\.png', srcset_url)
                                alt_name = alt_name_match.group(2) if alt_name_match else f"{pokemon_name}-Alt"
                                alt_name = f"{pokemon_name}-{alt_name}"  # Attach main name

                                # Extract image URL
                                img_url = img_tag['src']
                                save_path = images_folder / f"{alt_name}.png"
                                download_image(img_url, save_path)
                                pokemon_data.append((alt_name, img_url))

                        i += 1  # Move to next row

            elif len(cells) > 1:
                # Normal Pokémon without alternate forms
                img_tag = cells[1].find('img') if len(cells) > 1 else cells[0].find('img')
                pokemon_name = img_tag.get('alt', 'Unknown') if img_tag else 'Unknown'

                if img_tag and 'src' in img_tag.attrs:
                    img_url = img_tag['src']
                    save_path = images_folder / f"{pokemon_name}.png"
                    download_image(img_url, save_path)
                    pokemon_data.append((pokemon_name, img_url))

                i += 1
            else:
                i += 1

    return pokemon_data
