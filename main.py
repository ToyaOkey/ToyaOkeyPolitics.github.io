import os
import re
import markdown
import shutil
import config

# Set your Obsidian vault and output HTML folder
obsidian_vault_path = config.FILE_PATH  # Update this!
output_html_path = config.EXPORT_PATH # Output HTML folder
images_folder = "Images"  # Folder containing images (relative to vault)

# make sure output folder exists 
os.makedirs(output_html_path, exist_ok=True)

# dictionary to map markdown files
md_to_html_map = {}

# pass the map of the markdown files
for root, _, files in os.walk(obsidian_vault_path):
    # iteerate through all the files in the vault
    for file in files:
        # check if the file is a markdown file
        if file.endswith(".md"):
            # get the relative path of the file
            md_relative_path = os.path.relpath(os.path.join(root, file), obsidian_vault_path)
            # get the relative path of the html file (to be replaced in proper structure)
            html_relative_path = md_relative_path.replace(".md", ".html")
            # store the mapping of the markdown file to the html file
            md_to_html_map[file.replace(".md", "")] = html_relative_path  # Store mapping


def get_relative_html_path(current_md_path, linked_note):

    """ Computes the relative path to another note in HTML format. """
    # Check if the linked note exists in the map
    if linked_note in md_to_html_map:
        # Get the relative path to the linked note
        linked_html_path = md_to_html_map[linked_note]
        # Compute relative path from current note to linked note
        relative_link = os.path.relpath(linked_html_path, os.path.dirname(current_md_path))
        # Ensure forward slashes for web compatibility
        return relative_link.replace("\\", "/")  # Ensure forward slashes for web compatibility
    return f"{linked_note}.html"  # Fallback if the file isn't found

def get_relative_image_path(current_md_path, image_name):
    """ Computes relative path for images to ensure they work across folders. """
    # Check if the image exists in the Images folder
    image_path = os.path.join(obsidian_vault_path, images_folder, image_name)
    # If the image exists, compute the relative path
    if os.path.exists(image_path):
        # Compute relative path from current note to image
        relative_path = os.path.relpath(image_path, os.path.dirname(current_md_path))
        # Ensure forward slashes for web compatibility
        return relative_path.replace("\\", "/")  
    return f"{images_folder}/{image_name}"  # Fallback if the image is missing

def convert_obsidian_to_html(content, current_md_path):
    # Get relative path to the CSS file for styling
    relative_css_path = os.path.relpath(os.path.join(obsidian_vault_path, "styles.css"), os.path.dirname(current_md_path)).replace("\\", "/")

    # Convert image links ![[image.png]] to correct relative HTML <img> tags
    def image_replacer(match):
        # Extract the image name
        image_name = match.group(1)
        # Compute relative path to the image 
        relative_image_path = get_relative_image_path(current_md_path, image_name)
        # Return the HTML <img> tag and correct politics for output 
        return f'<img src="{relative_image_path.replace("Politics", "output")}" alt="{image_name}">'

    # Convert internal links [[note]] or [[note|alias]] to HTML <a> tags
    def link_replacer(match):
        # Extract the linked note and alias (if any)
        linked_note, alias = match.groups() if "|" in match.group(0) else (match.group(1), match.group(1))
        # Compute relative path to the linked note
        relative_link = get_relative_html_path(current_md_path, linked_note)
        # Return the HTML <a> tag with the correct alias and politics for output 
        return f'<a href="{relative_link}">{alias}</a>'
    
    # Replace all image and internal links in the content 
    content = re.sub(r'!\[\[([^\]]+)\]\]', image_replacer, content)
    content = re.sub(r'\[\[([^\]|]+)\|?([^\]]*)\]\]', link_replacer, content)


    # Convert Markdown to HTML
    html_content = markdown.markdown(
    content, 
    extensions=['markdown.extensions.extra'], 
    output_format='html5', 
    enable_attributes=False
)    # Wrap in a full HTML document
    
    # base html for each file 
    full_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{os.path.basename(current_md_path).replace('.md', '')}</title>
        <link rel="stylesheet" href="{relative_css_path.replace("Politics", "")}">
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&display=swap" rel="stylesheet">
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    return full_html

# Convert all Markdown files in the Obsidian vault to HTML
for root, _, files in os.walk(obsidian_vault_path):
    # Iterate through all files in the vault 
    for file in files:
        # Check if the file is a Markdown file
        if file.endswith(".md"):
            # Get the full path to the Markdown file 
            file_path = os.path.join(root, file)
            # Get the relative path to the Markdown file
            relative_md_path = os.path.relpath(file_path, obsidian_vault_path)
            # Get the relative path to the HTML file
            output_html_file = os.path.join(output_html_path, relative_md_path.replace(".md", ".html"))

            # Ensure parent directories exist
            os.makedirs(os.path.dirname(output_html_file), exist_ok=True)

            # Read Markdown content
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Convert to HTML
            converted_html = convert_obsidian_to_html(content, relative_md_path)

            # Save to the new HTML file
            with open(output_html_file, "w", encoding="utf-8") as f:
                # Write the converted HTML content to the new file 
                f.write(converted_html)
# Copy Images folder to the output HTML folder 
source_images_folder = os.path.join(obsidian_vault_path, images_folder)
target_images_folder = os.path.join(output_html_path, images_folder)

# Check if the Images folder exists 
if os.path.exists(source_images_folder):
    # Copy the Images folder to the output HTML folder
    shutil.copytree(source_images_folder, target_images_folder, dirs_exist_ok=True)
else:
    print("⚠️ No Images folder found. Skipping image copy.")
print("Conversion completed successfully! Markdown files now reference images and internal notes correctly in HTML. :D")
print(f"➡️ HTML files saved to: {output_html_path}")