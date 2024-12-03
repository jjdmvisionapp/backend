import hashlib


# ChatGPT
def get_image_hash(file_path):
    hash_sha256 = hashlib.sha256()

    # Open the file in binary mode to read its contents
    with open(file_path, 'rb') as file:
        # Read the image file in chunks to avoid memory issues with large files
        chunk_size = 8192  # 8KB chunks
        while chunk := file.read(chunk_size):
            hash_sha256.update(chunk)

    # Return the hexadecimal hash
    return hash_sha256.hexdigest()
