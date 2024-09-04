import os
import pandas as pd
from mpmath import convert
from tqdm import tqdm
from pathlib import Path

# Assuming images are stored in subdirectories named after 'item_order'
base_html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{product_title}</title>
</head>
<body>
    <div>
        <a href="{prev_link}">Previous</a> || <a href="{next_link}">Next</a>
    </div>
    <h1>No.{item_order}</h1>
    <h2>{product_title}</h2>
    <p><strong>Price:</strong> {product_price}</p>
    <p><strong>Rating:</strong> {product_rate}</p>
    <p><strong>Number Rating & Review:</strong> ({number_rating})</p>
    <p><strong>Number bought lately:</strong> ({number_bought_rating})</p>
    <p><strong>Number bought in 30 days:</strong> ({number_bought_in_30days})</p>
    <p><strong>Stock Number:</strong> {stock_number}</p>
    <p><strong>Description:</strong> {description}</p>
    <div>
        <h3>Parameters:</h3>
        <ul>
            {parameters}
        </ul>
    </div>
    <div>
        <h3>Images:</h3>
        {image_gallery}
    </div>
</body>
</html>
"""


# Function to generate the HTML content for each row
def generate_html_content(
        root_dir: str,
        output_dir: str,
        row,
        prev_row,
        next_row
):
    # Parameters in HTML format
    parameters = ''.join([f"<li>{key}: {value}</li>" for key, value in eval(row['parameters']).items()])

    # Images
    images_dir = os.path.join(root_dir, "images")
    product_sub_dir_prefix = f"{row['item_order'] - 1}__"
    product_sub_dir = [subdir for subdir in os.listdir(images_dir) if subdir.startswith(product_sub_dir_prefix)]
    if not product_sub_dir:
        image_gallery = "No images"
    else:
        product_images_dir = Path(
            os.path.join(images_dir, product_sub_dir[0])
        )
        # Use Path.rglob() to find all files
        all_files = list(product_images_dir.rglob('*'))
        image_files = [str(file) for file in all_files if file.is_file()]
        image_files_relative = [img_path.split(root_dir)[1] for img_path in image_files]
        image_gallery = ''.join(
            [f'<img src="..{img}" alt="{row["product_title"]}" style="width:600px;">' for img in image_files_relative])

    # Navigation Links
    prev_link = f'{prev_row["item_order"]}.html' if prev_row is not None else '#'
    next_link = f'{next_row["item_order"]}.html' if next_row is not None else '#'

    # Filling in the template
    html_content = base_html_template.format(
        item_order=row['item_order'],
        product_title=row['product_title'],
        product_price=row['product_price'],
        product_rate=row['product_rate'] if pd.notna(row['product_rate']) else 'N/A',
        number_rating=row['number_rating'] if pd.notna(row['number_rating']) else 'No ratings',
        stock_number=row['stock_number'] if pd.notna(row['stock_number']) else 'N/A',
        number_bought_rating=row['number_bought_rating'] if pd.notna(row['number_bought_rating']) else 'N/A',
        number_bought_in_30days=row['number_bought_in_30days'] if pd.notna(row['number_bought_in_30days']) else 'N/A',
        description=row['description'],
        parameters=parameters,
        image_gallery=image_gallery,
        prev_link=prev_link,
        next_link=next_link
    )

    # Saving HTML file
    output_file = os.path.join(output_dir, f"{row['item_order']}.html")
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(html_content)


if __name__ == '__main__':
    # Load the Excel file
    ROOT_DIR = "/home/yujiema/Videos/副业/allegro/GREENWORKS_data"
    file_path = os.path.join(ROOT_DIR, '格力博(GREENWORKS)户外工具_数据.xlsx')
    # Directory where HTML files will be saved
    output_dir = os.path.join(ROOT_DIR, 'webpages_ALL_products')
    os.makedirs(output_dir, exist_ok=True)

    df = pd.read_excel(file_path)

    # Display the first few rows to understand the structure of the data
    print(df.head())
    print(df.columns)

    # # Filter TOP products
    # middle_columns = df.columns[3:7]
    # df_sorted = df.sort_values(by=middle_columns.tolist(), ascending=[False] * len(middle_columns))
    # df_sorted = df_sorted.dropna(subset=middle_columns)
    # df_sorted = df_sorted.sort_values(by='item_order', ascending=True)
    # print(df_sorted)
    # data_frame = df_sorted

    data_frame = df
    # Iterate over DataFrame rows and generate HTML pages
    for idx in tqdm(range(len(data_frame))):
        current_row = data_frame.iloc[idx]
        prev_row = data_frame.iloc[idx - 1] if idx > 0 else None
        next_row = data_frame.iloc[idx + 1] if idx < len(data_frame) - 1 else None

        generate_html_content(
            root_dir=ROOT_DIR,
            output_dir=output_dir,
            row=current_row,
            prev_row=prev_row,
            next_row=next_row
        )

    print(output_dir)
