def _is_valid_file_type(data, signature):
    """
    :param data: file-like object
    :param signature: expected signature
    """
    size = len(signature)
    return data.read(size) == signature


def is_valid_png(data):
    return _is_valid_file_type(data, b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A")


def is_valid_gif(data):
    return _is_valid_file_type(data, b"GIF89a")
