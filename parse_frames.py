import sys

# Basic script to parse frames from input file or stdin
# Each frame is 16 bytes starting with 0xAA
# CRC algorithm replicates the one in motornet6_full.cs

# CRC tables from C# file
CRCTABLE_LO = [
    0, 192, 193, 1, 195, 3, 2, 194, 198, 6,
    7, 199, 5, 197, 196, 4, 204, 12, 13, 205,
    15, 207, 206, 14, 10, 202, 203, 11, 201, 9,
    8, 200, 216, 24, 25, 217, 27, 219, 218, 26,
    30, 222, 223, 31, 221, 29, 28, 220, 20, 212,
    213, 21, 215, 23, 22, 214, 210, 18, 19, 211,
    17, 209, 208, 16, 240, 48, 49, 241, 51, 243,
    242, 50, 54, 246, 247, 55, 245, 53, 52, 244,
    60, 252, 253, 61, 255, 63, 62, 254, 250, 58,
    59, 251, 57, 249, 248, 56, 40, 232, 233, 41,
    235, 43, 42, 234, 238, 46, 47, 239, 45, 237,
    236, 44, 228, 36, 37, 229, 39, 231, 230, 38,
    34, 226, 227, 35, 225, 33, 32, 224, 160, 96,
    97, 161, 99, 163, 162, 98, 102, 166, 167, 103,
    165, 101, 100, 164, 108, 172, 173, 109, 175, 111,
    110, 174, 170, 106, 107, 171, 105, 169, 168, 104,
    120, 184, 185, 121, 187, 123, 122, 186, 190, 126,
    127, 191, 125, 189, 188, 124, 180, 116, 117, 181,
    119, 183, 182, 118, 114, 178, 179, 115, 177, 113,
    112, 176, 80, 144, 145, 81, 147, 83, 82, 146,
    150, 86, 87, 151, 85, 149, 148, 84, 156, 92,
    93, 157, 95, 159, 158, 94, 90, 154, 155, 91,
    153, 89, 88, 152, 136, 72, 73, 137, 75, 139,
    138, 74, 78, 142, 143, 79, 141, 77, 76, 140,
    68, 132, 133, 69, 135, 71, 70, 134, 130, 66,
    67, 131, 65, 129, 128, 64
]

CRCTABLE_HI = [
    0, 193, 129, 64, 1, 192, 128, 65, 1, 192,
    128, 65, 0, 193, 129, 64, 1, 192, 128, 65,
    0, 193, 129, 64, 0, 193, 129, 64, 1, 192,
    128, 65, 1, 192, 128, 65, 0, 193, 129, 64,
    0, 193, 129, 64, 1, 192, 128, 65, 0, 193,
    129, 64, 1, 192, 128, 65, 1, 192, 128, 65,
    0, 193, 129, 64, 1, 192, 128, 65, 0, 193,
    129, 64, 0, 193, 129, 64, 1, 192, 128, 65,
    0, 193, 129, 64, 1, 192, 128, 65, 1, 192,
    128, 65, 0, 193, 129, 64, 0, 193, 129, 64,
    1, 192, 128, 65, 1, 192, 128, 65, 0, 193,
    129, 64, 1, 192, 128, 65, 0, 193, 129, 64,
    0, 193, 129, 64, 1, 192, 128, 65, 1, 192,
    128, 65, 0, 193, 129, 64, 0, 193, 129, 64,
    1, 192, 128, 65, 0, 193, 129, 64, 1, 192,
    128, 65, 1, 192, 128, 65, 0, 193, 129, 64,
    0, 193, 129, 64, 1, 192, 128, 65, 1, 192,
    128, 65, 0, 193, 129, 64, 1, 192, 128, 65,
    0, 193, 129, 64, 0, 193, 129, 64, 1, 192,
    128, 65, 0, 193, 129, 64, 1, 192, 128, 65,
    1, 192, 128, 65, 0, 193, 129, 64, 1, 192,
    128, 65, 0, 193, 129, 64, 0, 193, 129, 64,
    1, 192, 128, 65, 1, 192, 128, 65, 0, 193,
    129, 64, 0, 193, 129, 64, 1, 192, 128, 65,
    0, 193, 129, 64, 1, 192, 128, 65, 1, 192,
    128, 65, 0, 193, 129, 64
]

CRCTABLE_LO = CRCTABLE_LO[:256]
CRCTABLE_HI = CRCTABLE_HI[:256]


def crc_special(frame):
    b = 60
    b2 = 127
    for byte in frame[:14]:
        num = b ^ byte
        b = (b2 ^ CRCTABLE_HI[num]) & 0xFF
        b2 = CRCTABLE_LO[num]
    return b, b2


def crc_simple(frame):
    total = sum(frame[:14])
    return (total >> 8) & 0xFF, total & 0xFF


def parse_line(line):
    parts = line.strip().split()
    try:
        start = parts.index('Data:') + 1
    except ValueError:
        return None
    bytes_str = parts[start:]
    if len(bytes_str) != 16:
        return None
    frame = [int(x, 16) for x in bytes_str]
    if frame[0] != 0xAA:
        return None
    if frame[1] & 0x80:
        crc = crc_special(frame)
    else:
        crc = crc_simple(frame)
    good = (frame[14] == crc[0] and frame[15] == crc[1])
    return frame, good


def main():
    for line in sys.stdin:
        res = parse_line(line)
        if not res:
            continue
        frame, good = res
        print('Frame', frame, 'CRC OK' if good else 'CRC FAIL')

if __name__ == '__main__':
    main()
