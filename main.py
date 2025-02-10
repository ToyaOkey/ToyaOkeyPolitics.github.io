import os
import re
import markdown
import shutil
import config

# Set your Obsidian vault and output HTML folder
obsidian_vault_path = config.FILE_PATH  # Update this!
output_html_path = config.EXPORT_PATH # Output HTML folder
images_folder = "Images"  # Folder containing images (relative to vault)

# Ensure output directory exists
os.makedirs(output_html_path, exist_ok=True)

# Dictionary to map markdown file paths to HTML file paths
md_to_html_map = {}

# Step 1: First pass to map Markdown filenames to relative HTML paths
for root, _, files in os.walk(obsidian_vault_path):
    for file in files:
        if file.endswith(".md"):
            md_relative_path = os.path.relpath(os.path.join(root, file), obsidian_vault_path)
            html_relative_path = md_relative_path.replace(".md", ".html")
            md_to_html_map[file.replace(".md", "")] = html_relative_path  # Store mapping

# Function to determine the correct relative path for internal links
def get_relative_html_path(current_md_path, linked_note):
    """ Computes the relative path to another note in HTML format. """
    if linked_note in md_to_html_map:
        linked_html_path = md_to_html_map[linked_note]
        relative_link = os.path.relpath(linked_html_path, os.path.dirname(current_md_path))
        return relative_link.replace("\\", "/")  # Ensure forward slashes for web compatibility
    return f"{linked_note}.html"  # Fallback if the file isn't found

# Function to find correct relative path for images
def get_relative_image_path(current_md_path, image_name):
    """ Computes relative path for images to ensure they work across folders. """
    image_path = os.path.join(obsidian_vault_path, images_folder, image_name)
    if os.path.exists(image_path):
        relative_path = os.path.relpath(image_path, os.path.dirname(current_md_path))
        return relative_path.replace("\\", "/")  # Web-compatible paths
    return f"{images_folder}/{image_name}"  # Fallback if the image is missing

# Function to convert Obsidian Markdown to HTML with correct links
def convert_obsidian_to_html(content, current_md_path):
        # Convert image links ![[image.png]] to correct relative HTML <img> tags
    relative_css_path = os.path.relpath(os.path.join(obsidian_vault_path, "styles.css"), os.path.dirname(current_md_path)).replace("\\", "/")

    def image_replacer(match):
        # print(match)
        image_name = match.group(1)
        relative_image_path = get_relative_image_path(current_md_path, image_name)
        return f'<img src="{relative_image_path.replace("Politics", "output")}" alt="{image_name}">'

    # Convert internal links [[note]] or [[note|alias]] to HTML <a> tags
    def link_replacer(match):
        linked_note, alias = match.groups() if "|" in match.group(0) else (match.group(1), match.group(1))
        relative_link = get_relative_html_path(current_md_path, linked_note)
        return f'<a href="{relative_link}">{alias}</a>'

    content = re.sub(r'!\[\[([^\]]+)\]\]', image_replacer, content)
    content = re.sub(r'\[\[([^\]|]+)\|?([^\]]*)\]\]', link_replacer, content)


    # Convert Markdown to HTML
    html_content = markdown.markdown(
    content, 
    extensions=['markdown.extensions.extra'], 
    output_format='html5', 
    enable_attributes=False
)    # Wrap in a full HTML document

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
        <button id="dark-mode-toggle">🌙 Toggle Dark Mode</button> 
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    return full_html

# Step 2: Convert all Markdown files to HTML with correct relative paths
for root, _, files in os.walk(obsidian_vault_path):
    for file in files:
        if file.endswith(".md"):
            file_path = os.path.join(root, file)
            relative_md_path = os.path.relpath(file_path, obsidian_vault_path)
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
                f.write(converted_html)

source_images_folder = os.path.join(obsidian_vault_path, images_folder)
target_images_folder = os.path.join(output_html_path, images_folder)

if os.path.exists(source_images_folder):
    shutil.copytree(source_images_folder, target_images_folder, dirs_exist_ok=True)
    # print(f"✅ Images folder copied to: {target_images_folder}")
else:
    print("⚠️ No Images folder found. Skipping image copy.")

print("✅ Conversion completed successfully! Markdown files now reference images and internal notes correctly in HTML.")
print(f"➡️ HTML files saved to: {output_html_path}")