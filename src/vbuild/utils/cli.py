from rich_toolkit.styles import TaggedStyle
from rich_toolkit.toolkit import RichToolkit, RichToolkitTheme


def get_rich_toolkit(json_output: bool = False) -> RichToolkit:
    theme = RichToolkitTheme(
        style=TaggedStyle(tag_width=5),
        theme={
            "tag.title": "white on #009485",
            "error": "red",
            "success": "green",
        },
    )
    return RichToolkit(theme=theme, mode="json" if json_output else "human")
