#!/usr/bin/env python3
import io
import sys
from collections import namedtuple
from struct import unpack

from PIL import Image

rdata = sys.stdin.buffer.read()

CupsRas3 = namedtuple(
    # Documentation at https://www.cups.org/doc/spec-raster.html
    'CupsRasHeader',
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


# TODO: Rotations
# TODO: Paper sizes

def read_ras3(rdata):
    magic = unpack('@4s', rdata[0:4])[0]

    if magic != b'RaS3' and magic != b'3SaR':
        raise ValueError("This is not in RaS3 format")
    rdata = rdata[4:]
    pages = []

    while rdata:
        struct_data = unpack(
            '@64s 64s 64s 64s I I I I I II IIII I I I II I I I I I I I I II I I I I I I I I I I I I I '
            'I I I f ff ffff IIIIIIIIIIIIIIII ffffffffffffffff 64s 64s 64s 64s 64s 64s 64s 64s 64s 64s '
            '64s 64s 64s 64s 64s 64s 64s 64s 64s',
            rdata[0:1796]
        )
        data = [
            b.decode().rstrip('\x00') if isinstance(b, bytes) else b
            for b in struct_data
        ]
        header = CupsRas3._make(data)

        imgdata = rdata[1796:1796 + (header.cupsWidth * header.cupsHeight * header.cupsBitsPerPixel // 8)]
        pages.append((header, imgdata))
        rdata = rdata[1796 + (header.cupsWidth * header.cupsHeight * header.cupsBitsPerPixel // 8):]

    return pages


pages = read_ras3(rdata)

for i, datatuple in enumerate(pages):
    (header, imgdata) = datatuple
    if header.cupsColorSpace != 0 or header.cupsNumColors != 1:
        raise ValueError('Invalid color space, only monocolor supported')

    im = Image.new("L", (header.cupsWidth, header.cupsHeight))
    pixels = im.load()
    for i, b in enumerate(imgdata):
        pixels[i % header.cupsWidth, i // header.cupsWidth] = b
    im = im.convert('1')

    bbuffer = io.BytesIO()
    im.save(bbuffer, format='PCX')
    pcximg = bbuffer.getvalue()

    #sys.stdout.buffer.write(b'<CB>')
    sys.stdout.buffer.write('<RC0,0><NR><pcx><G{}>'.format(len(pcximg)).encode())
    sys.stdout.buffer.write(pcximg)
    if header.CutMedia in (1, 2, 3) and i == len(pages) - 1:  # Cut after file/job/set
        sys.stdout.buffer.write(b'<p>')
    elif header.CutMedia == 4:  # Cut after page
        sys.stdout.buffer.write(b'<p>')
    else:
        sys.stdout.buffer.write(b'<q>')
    #sys.stdout.buffer.write(b'0x04')
