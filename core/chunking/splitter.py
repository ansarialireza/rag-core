def chunk_text(text: str, chunk_size: int, chunk_overlap: int):
    if not text:
        return []
    if chunk_size <= 0:
        raise ValueError('chunk_size must be greater than zero.')
    if chunk_overlap < 0:
        raise ValueError('chunk_overlap must be zero or greater.')
    if chunk_overlap >= chunk_size:
        raise ValueError('chunk_overlap must be smaller than chunk_size.')

    text = text.strip()
    if not text:
        return []

    step = chunk_size - chunk_overlap
    chunks = []
    start = 0
    index = 0

    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunk = text[start:end]
        if not chunk.strip():
            break
        chunks.append({
            'index': index,
            'start_char': start,
            'end_char': end,
            'content': chunk,
        })
        if end == len(text):
            break
        start += step
        index += 1

    return chunks
