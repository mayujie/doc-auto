# https://developer.allegro.pl/tutorials/basic-information-VL6YelvVKTn
# https://developer.allegro.pl/
import os
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from typing import List, Tuple
import subprocess
import time
from urllib.parse import urlparse


def download_images(df: pd.DataFrame, save_images_dir: str = "images"):
    # Create directory to save images if it doesn't exist
    if not os.path.exists(save_images_dir):
        os.makedirs(save_images_dir)

    count_images = 0
    # Iterate over each row using itertuples()
    for row in df.itertuples(index=True, name='Pandas'):
        # print(f"Index: {row.Index}, order {row.item_order}, product_title: {row.product_title}")
        if not row.images_url:  # If the list is empty, do nothing
            continue

        save_item_image_dir = os.path.join(save_images_dir, f'{row.Index}__{row.product_title}')
        if not os.path.exists(save_item_image_dir):
            os.makedirs(save_item_image_dir)

        for i, url in enumerate(row.images_url):
            # Extract the filename from the URL
            filename = os.path.basename(urlparse(url).path)
            img_path = os.path.join(save_item_image_dir, filename)
            # Check if the file already exists
            if os.path.exists(img_path):
                print(f"File already exists: {img_path}")
                continue  # Skip downloading if the file already exists
            try:
                # Use wget to download the image
                subprocess.run(['wget', url, '-P', save_item_image_dir, '-nc'], check=True)
                print(f"Downloaded: {url} to {img_path}")
                time.sleep(2)
                count_images += 1

                # img_name = os.path.join(save_item_image_dir, f'image_{i}.jpg')
                # response = requests.get(url)
                # response.raise_for_status()  # Check for HTTP errors
                # with open(img_name, 'wb') as file:
                #     file.write(response.content)
                # print(f"Downloaded: {img_name}")

            except requests.exceptions.RequestException as e:
                print(f"Failed to download {url}: {e}")

    print(f"## Total number of image url: [{count_images}]")


# Function to convert JSON string to a dictionary
def list_pair_to_dict(json_str):
    # Parse the JSON string into a Python list
    data = json.loads(json_str)

    # Initialize an empty dictionary to hold the final key-value pairs
    result_dict = {}

    # Loop through the list with a step of 2 to get pairs of items
    for i in range(0, len(data), 2):
        # Extract the key and value from consecutive elements
        key = data[i]["params"]
        value = data[i + 1]["params"]

        # Add the key-value pair to the dictionary
        result_dict[key] = value

    return result_dict


def extract_img_urls(html_content):
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    # Find all img tags
    img_tags = soup.find_all('img')
    # Extract only the URLs

    img_urls = []
    for img in img_tags:
        # Get 'data-src' if present, otherwise get 'src'
        url = img.get('data-src', img.get('src'))
        if url:
            img_urls.append(url)

    return img_urls


def run_process(file_path: str, save_root_dir: str):
    df = pd.read_excel(file_path)
    df = df.drop(df.columns[[1, 2, 3]], axis=1)
    df = df.rename(columns={'web-scraper-order': 'item_order'})
    df = df.rename(columns={'product title': 'product_title'})
    df = df.rename(columns={'product price': 'product_price'})
    df = df.rename(columns={'product rate': 'product_rate'})
    df = df.rename(columns={'product number rating': 'number_rating'})
    df = df.rename(columns={'bought lately': 'number_bought_rating'})
    df = df.rename(columns={'bought num': 'number_bought_in_30days'})
    df = df.rename(columns={'max to buy': 'stock_number'})

    # Apply the function to each row in the column with string list
    df['parameters'] = df['params'].apply(list_pair_to_dict)
    df = df.drop(columns=['params'])

    df['item_order'] = df['item_order'].str.replace(r'\d+-', '', regex=True)
    df['description'] = df['description'].str.replace('allegro', '', case=False)

    # Apply the function to the 'HTML_Content' column
    df['images_url'] = df['images'].apply(extract_img_urls)
    # Count the number of non-empty lists in 'column_name'
    non_empty_count = df[df['images_url'].apply(lambda x: len(x) > 0)].shape[0]
    print(f'Number of product with image url: {non_empty_count}')
    df = df.drop(columns=['images'])

    if not os.path.exists(save_root_dir):
        os.makedirs(save_root_dir)

    # Apply the download_images function to each row in the 'image_urls' column
    save_images_dir = os.path.join(save_root_dir, 'images')
    download_images(df=df, save_images_dir=save_images_dir)
    df = df.drop(columns=['images_url'])

    save_filename_final = os.path.join(save_root_dir, '格力博(GREENWORKS)户外工具_数据.xlsx')
    df.to_excel(save_filename_final, index=False)
    print("### Finished ###")


if __name__ == '__main__':
    root_dir = '/home/yujiema/Videos/side_jb'
    save_root_dir = '/home/yujiema/Videos/side_jb/GREENWORKS_data'
    filename = 'ecommerce.xlsx'
    # filename = 'ecom_data.xlsx'
    file_path = os.path.join(root_dir, filename)
    run_process(file_path=file_path, save_root_dir=save_root_dir)
