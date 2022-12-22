import struct


def numpy2tiff(image, path):
    def tiff_tag(tag_code, datatype, values):
        types = {'<H': 3, '<L': 4, '<Q': 16}
        datatype_code = types[datatype]
        number = 1 if isinstance(values, int) else len(values)
        if number == 1:
            values_bytes = struct.pack(datatype, values)
        else:
            values_bytes = struct.pack('<' + (datatype[-1:] * number), *values)
        tag_bytes = struct.pack('<HHQ', tag_code, datatype_code, number) + values_bytes
        tag_bytes += b'\x00' * (20 - len(tag_bytes))
        return tag_bytes

    image_bytes = image.shape[0] * image.shape[1] * image.shape[2]
    with open(path, 'wb+') as f:
        image.reshape((image_bytes,))
        f.write(b'II')
        f.write(struct.pack('<H', 43))  # Version number
        f.write(struct.pack('<H', 8))  # Bytesize of offsets
        f.write(struct.pack('<H', 0))  # always zero
        f.write(struct.pack('<Q', 16 + image_bytes))  # Offset to IFD
        for offset in range(0, image_bytes, 2 ** 20):
            f.write(image[offset:offset + 2 ** 20].tobytes())
        f.write(struct.pack('<Q', 8))  # Number of tags in IFD
        f.write(tiff_tag(256, '<L', image.shape[1]))  # ImageWidth tag
        f.write(tiff_tag(257, '<L', image.shape[0]))  # ImageLength tag
        f.write(tiff_tag(258, '<H', (8, 8, 8)))  # BitsPerSample tag
        f.write(tiff_tag(262, '<H', 2))  # PhotometricInterpretation tag
        f.write(tiff_tag(273, '<H', 16))  # StripOffsets tag
        f.write(tiff_tag(277, '<H', 3))  # SamplesPerPixel
        f.write(tiff_tag(278, '<Q', image_bytes // 8192))  # RowsPerStrip
        f.write(tiff_tag(279, '<Q', image_bytes))  # StripByteCounts
        f.write(struct.pack('<Q', 0))  # Offset to next IFD
