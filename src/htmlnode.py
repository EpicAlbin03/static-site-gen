class HTMLNode:
    def __init__(
        self,
        tag: str | None = None,
        value: str | None = None,
        children: list["HTMLNode"] | None = None,
        props: dict[str, str] | None = None,
    ):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self) -> str:
        raise NotImplemented

    def props_to_html(self) -> str:
        if self.props is None:
            return ""
        return " " + " ".join(f'{key}="{val}"' for key, val in self.props.items())

    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"


class LeafNode(HTMLNode):
    def __init__(
        self,
        tag: str | None,
        value: str,
        props: dict[str, str] | None = None,
    ):
        super().__init__(tag, value, None, props)
        self.value = value
        self.tag = tag

    def to_html(self) -> str:
        if not self.tag:
            return self.value
        if self.tag == "img":
            return f"<{self.tag}{self.props_to_html()}>"
        if len(self.value) < 1:
            raise ValueError("missing value")
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"

    def __repr__(self):
        return f"LeafNode({self.tag}, {self.value}, {self.props})"


class ParentNode(HTMLNode):
    def __init__(
        self,
        tag: str,
        children: list["HTMLNode"],
        props: dict[str, str] | None = None,
    ):
        super().__init__(tag, None, children, props)
        self.tag = tag
        self.children = children

    def to_html(self) -> str:
        if not self.tag:
            raise ValueError("missing tag")
        if len(self.children) < 1:
            raise ValueError("missing children")

        children_html = ""
        for child in self.children:
            children_html += child.to_html()
        return f"<{self.tag}{self.props_to_html()}>{children_html}</{self.tag}>"

    def __repr__(self):
        return f"ParentNode({self.tag}, {self.children}, {self.props})"
