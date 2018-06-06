#!/usr/bin/env python3
import sys
from collections import namedtuple
from struct import unpack

import numpy as np
from PIL import Image

CupsRas3 = namedtuple(
    # Documentation at https://www.cups.org/doc/spec-raster.html
    'CupsRas3',
    'MediaClass MediaColor MediaType OutputType AdvanceDistance AdvanceMedia Collate CutMedia Duplex HWResolutionH '
    'HWResolutionV ImagingBoundingBoxL ImagingBoundingBoxB ImagingBoundingBoxR ImagingBoundingBoxT '
    'InsertSheet Jog LeadingEdge MarginsL MarginsB ManualFeed MediaPosition MediaWeight MirrorPrint '
    'NegativePrint NumCopies Orientation OutputFaceUp PageSizeW PageSizeH Separations TraySwitch Tumble cupsWidth '
    'cupsHeight cupsMediaType cupsBitsPerColor cupsBitsPerPixel cupsBitsPerLine cupsColorOrder cupsColorSpace '
    'cupsCompression cupsRowCount cupsRowFeed cupsRowStep cupsNumColors cupsBorderlessScalingFactor cupsPageSizeW '
    'cupsPageSizeH cupsImagingBBoxL cupsImagingBBoxB cupsImagingBBoxR cupsImagingBBoxT cupsInteger1 cupsInteger2 '
    'cupsInteger3 cupsInteger4 cupsInteger5 cupsInteger6 cupsInteger7 cupsInteger8 cupsInteger9 cupsInteger10 '
    'cupsInteger11 cupsInteger12 cupsInteger13 cupsInteger14 cupsInteger15 cupsInteger16 cupsReal1 cupsReal2 '
    'cupsReal3 cupsReal4 cupsReal5 cupsReal6 cupsReal7 cupsReal8 cupsReal9 cupsReal10 cupsReal11 cupsReal12 '
    'cupsReal13 cupsReal14 cupsReal15 cupsReal16 cupsString1 cupsString2 cupsString3 cupsString4 cupsString5 '
    'cupsString6 cupsString7 cupsString8 cupsString9 cupsString10 cupsString11 cupsString12 cupsString13 cupsString14 '
    'cupsString15 cupsString16 cupsMarkerType cupsRenderingIntent cupsPageSizeName'
)


def read_ras3(rdata):
    if not rdata:
        raise ValueError('No data received')

    # Check for magic word (either big-endian or little-endian)
    magic = unpack('@4s', rdata[0:4])[0]
    if magic != b'RaS3' and magic != b'3SaR':
        raise ValueError("This is not in RaS3 format")
    rdata = rdata[4:]  # Strip magic word
    pages = []

    while rdata:  # Loop over all pages
        struct_data = unpack(
            '@64s 64s 64s 64s I I I I I II IIII I I I II I I I I I I I I II I I I I I I I I I I I I I '
            'I I I f ff ffff IIIIIIIIIIIIIIII ffffffffffffffff 64s 64s 64s 64s 64s 64s 64s 64s 64s 64s '
            '64s 64s 64s 64s 64s 64s 64s 64s 64s',
            rdata[0:1796]
        )
        data = [
            # Strip trailing null-bytes of strings
            b.decode().rstrip('\x00') if isinstance(b, bytes) else b
            for b in struct_data
        ]
        header = CupsRas3._make(data)

        # Read image data of this page into a bytearray
        imgdata = rdata[1796:1796 + (header.cupsWidth * header.cupsHeight * header.cupsBitsPerPixel // 8)]
        pages.append((header, imgdata))

        # Remove this page from the data stream, continue with the next page
        rdata = rdata[1796 + (header.cupsWidth * header.cupsHeight * header.cupsBitsPerPixel // 8):]

    return pages


pages = read_ras3(sys.stdin.buffer.read())

for i, datatuple in enumerate(pages):
    (header, imgdata) = datatuple

    if header.cupsColorSpace != 0 or header.cupsNumColors != 1:
        raise ValueError('Invalid color space, only monocolor supported')

    npdata = np.frombuffer(imgdata, dtype=np.uint8)
    npixels = npdata.reshape((header.cupsHeight, header.cupsWidth)).transpose()

    im = Image.fromarray(npixels, 'L')
    im = im.convert('1', dither=1)
    sys.stdout.buffer.write(b'<CB>')
    npixels = np.array(im.getdata()).reshape((header.cupsWidth, header.cupsHeight))
    for yoffset in range(0, npixels.shape[1], 8):
        row_octet = np.zeros(npixels.shape[0], dtype=np.uint8)
        for j in range(8):
            row_blacks = (npixels[:, min(yoffset + j, npixels.shape[1] -1)] < 128).astype(np.uint8)
            row_octet = np.bitwise_or(row_octet, np.left_shift(row_blacks, 7 - j))
        if row_octet.any():
            # FGL: <RCy,x>: Move to correct position
            # FGL: <Gnn>: nn bytes of graphics are followinga
            sys.stdout.buffer.write('<RC{},{}><G{}>'.format(yoffset, 0, row_octet.shape[0]).encode())
            sys.stdout.buffer.write(row_octet.tostring())

    if header.CutMedia in (1, 2, 3) and i == len(pages) - 1:  # Cut after last ticket of file/job/set
        sys.stdout.buffer.write(b'<p>')
    elif header.CutMedia == 4:  # Cut after page
        sys.stdout.buffer.write(b'<p>')
    else:  # Do not cut
        sys.stdout.buffer.write(b'<q>')
