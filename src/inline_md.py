from textnode import TextType, TextNode
import re
from typing import Callable


def split_nodes_delimiter(
    old_nodes: list[TextNode], delimiter: str, text_type: TextType
) -> list[TextNode]:
    new_nodes: list[TextNode] = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        split_nodes: list[TextNode] = []
        sections = old_node.text.split(delimiter)
        if len(sections) % 2 == 0:
            raise ValueError("invalid markdown, formatted section not closed")
        for i in range(len(sections)):
            if sections[i] == "":
                continue
            if i % 2 == 0:
                split_nodes.append(TextNode(sections[i], TextType.TEXT))
            else:
                split_nodes.append(TextNode(sections[i], text_type))
        new_nodes.extend(split_nodes)
    return new_nodes


def extract_markdown_images(text: str) -> list[tuple[str, str]]:
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)


def extract_markdown_links(text: str) -> list[tuple[str, str]]:
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)


def _split_nodes_markdown_element(
    old_nodes: list[TextNode],
    extract_func: Callable[[str], list[tuple[str, str]]],
    text_type: TextType,
    format_func: Callable[[tuple[str, str]], str],
) -> list[TextNode]:
    new_nodes: list[TextNode] = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        original_text = old_node.text
        elements = extract_func(original_text)
        if len(elements) == 0:
            new_nodes.append(old_node)
            continue
        for element in elements:
            markdown_text = format_func(element)
            sections = original_text.split(markdown_text, 1)
            if len(sections) != 2:
                raise ValueError(
                    f"invalid markdown, {text_type.value.lower()} section not closed"
                )
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            new_nodes.append(
                TextNode(
                    element[0],
                    text_type,
                    element[1],
                )
            )
            original_text = sections[1]
        if original_text != "":
            new_nodes.append(TextNode(original_text, TextType.TEXT))
    return new_nodes


def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    return _split_nodes_markdown_element(
        old_nodes,
        extract_markdown_images,
        TextType.IMAGE,
        lambda img: f"![{img[0]}]({img[1]})",
    )


def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    return _split_nodes_markdown_element(
        old_nodes,
        extract_markdown_links,
        TextType.LINK,
        lambda link: f"[{link[0]}]({link[1]})",
    )


def text_to_textnodes(text: str) -> list[TextNode]:
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes
