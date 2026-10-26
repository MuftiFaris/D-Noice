"""Profil intensitas dan histogram dihitung langsung dari piksel."""
def image_analysis(image, row=None):
    """Data grafik asli: profil satu baris dan histogram seluruh citra, tanpa library."""
    height, width = len(image), len(image[0])
    if row is None:
        row = height // 2
    if isinstance(row, bool) or not isinstance(row, int) or not 0 <= row < height:
        raise ValueError('Baris analisis di luar citra.')
    histogram = [0] * 256
    for y in range(height):
        for x in range(width):
            histogram[image[y][x]] += 1
    profile = []
    for x in range(width):
        profile.append(image[row][x])
    return dict(profile_row=row, profile=profile, histogram=histogram, pixel_count=height*width)
