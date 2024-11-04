

def escape_markdown_v2(text):
    """Экранирует специальные символы для MarkdownV2."""
    special_chars = r"_*[]()~`>#+-=|{}.!"
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text