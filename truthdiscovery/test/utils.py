def is_valid_png(data):
    """
    Return true if the first 8 bytes of the data match the special signature
    for PNG files.

    :param data: file-like object or bytes
    """
    signature = b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A"
    try:
        return data.read(8) == signature
    except AttributeError:
        return data[:8] == signature
