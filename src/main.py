import os
import shutil
from pathlib import Path
from blocks_md import markdown_to_html_node


def main():
    copy_files("static", "public")
    generate_pages_recursive("content", "template.html", "public")


def copy_files(src_dir: str, target_dir: str):
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)

    for filename in os.listdir(src_dir):
        from_path = os.path.join(src_dir, filename)
        dest_path = os.path.join(target_dir, filename)
        print(f" * {from_path} -> {dest_path}")
        if os.path.isfile(from_path):
            shutil.copy(from_path, dest_path)
        else:
            copy_files(from_path, dest_path)


def extract_title(markdown: str) -> str:
    lines = markdown.split("\n")
    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith("# ") and not stripped_line.startswith("## "):
            title = stripped_line[2:].strip()
            if title:
                return title
    raise ValueError("No h1 header found in markdown")


def generate_page(from_path: str, template_path: str, dest_path: str):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    with open(from_path, "r", encoding="utf-8") as f:
        markdown_content = f.read()
    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()

    html_node = markdown_to_html_node(markdown_content)
    html_content = html_node.to_html()
    title = extract_title(markdown_content)
    full_html = template_content.replace("{{ Title }}", title)
    full_html = full_html.replace("{{ Content }}", html_content)

    dest_dir = os.path.dirname(dest_path)
    if dest_dir and not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(full_html)


def generate_pages_recursive(
    dir_path_content: str, template_path: str, dest_dir_path: str
):
    for entry in os.listdir(dir_path_content):
        entry_path = os.path.join(dir_path_content, entry)
        if os.path.isfile(entry_path):
            if entry_path.endswith(".md"):
                html_filename = Path(entry).with_suffix(".html").name
                dest_file_path = os.path.join(dest_dir_path, html_filename)
                generate_page(entry_path, template_path, dest_file_path)
        else:
            dest_subdir = os.path.join(dest_dir_path, entry)
            generate_pages_recursive(entry_path, template_path, dest_subdir)


main()
