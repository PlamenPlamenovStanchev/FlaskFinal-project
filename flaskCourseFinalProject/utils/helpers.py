import base64

from werkzeug.exceptions import BadRequest


def decode_photo(path, encoded_string):
    with open(path, "wb") as f:
        try:
            f.write(base64.b64decode(encoded_string.encode("utf-8")))
        except Exception as ex:
            raise BadRequest("Invalid photo encoding")

encoded_file = "fjadjofosdfsdofojsdfsdjsdjfsdjofsdofsd;f,sdfds;f"