def read_file_with_fallback_encodings(
    file_path, encodings=["utf-8", "windows-1252", "iso-8859-1"]
):
    embedded_null_byte = False
    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as file:
                return file.read()
        except UnicodeDecodeError:
            continue
        except ValueError:
            embedded_null_byte = True
            continue
    if embedded_null_byte:
        raise Exception(f"Encountered null byte while decoding {file_path}")
    raise UnicodeDecodeError(
        f"Could not decode {file_path} with any of the specified encodings: {encodings}"
    )