import os
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT = (
    sys.argv[1]
    if len(sys.argv) > 1
    else os.path.join(BASE_DIR, "source-photo.jpeg")
)

OUTPUT = (
    sys.argv[2]
    if len(sys.argv) > 2
    else os.path.join(BASE_DIR, "source-prepped.png")
)


def prepare_photo(input_file, output_file):

    print("Loading:", input_file)

    # Load photo
    original = Image.open(input_file).convert("RGBA")

    # Remove background
    cutout = remove(original)

    rgb = np.array(cutout.convert("RGB"))
    alpha = np.array(cutout.getchannel("A"))

    # Find subject
    ys, xs = np.where(alpha > 30)

    if len(xs) == 0:
        raise ValueError("No subject detected.")

    min_x, max_x = xs.min(), xs.max()
    min_y, max_y = ys.min(), ys.max()

    person_width = max_x - min_x
    person_height = max_y - min_y

    print("Detected subject:", person_width, "x", person_height)

    # ----------------------------------------
    # Crop around upper body
    # ----------------------------------------

    crop_top = max(
        0,
        min_y - int(person_height * 0.08)
    )

    crop_bottom = min(
        alpha.shape[0],
        min_y + int(person_height * 0.78)
    )

    horizontal_pad = int(person_width * 0.18)

    crop_left = max(
        0,
        min_x - horizontal_pad
    )

    crop_right = min(
        alpha.shape[1],
        max_x + horizontal_pad
    )

    # Crop image
    rgb_crop = rgb[
        crop_top:crop_bottom,
        crop_left:crop_right
    ]

    alpha_crop = alpha[
        crop_top:crop_bottom,
        crop_left:crop_right
    ]

    # ----------------------------------------
    # Grayscale
    # ----------------------------------------

    gray = cv2.cvtColor(
        rgb_crop,
        cv2.COLOR_RGB2GRAY
    )

    # Smooth noise
    gray = cv2.bilateralFilter(
        gray,
        7,
        35,
        35
    )

    # ----------------------------------------
    # Contrast
    # ----------------------------------------

    subject_pixels = gray[
        alpha_crop > 30
    ]

    if len(subject_pixels) > 0:

        low, high = np.percentile(
            subject_pixels,
            [2, 96]
        )

        if high > low:

            gray = (
                gray.astype(np.float32) - low
            ) / (high - low)

            gray = np.clip(
                gray,
                0,
                1
            )

            gray = (
                gray * 255
            ).astype(np.uint8)

    # ----------------------------------------
    # Sharpen
    # ----------------------------------------

    blur = cv2.GaussianBlur(
        gray,
        (0, 0),
        1.2
    )

    gray = cv2.addWeighted(
        gray,
        1.3,
        blur,
        -0.3,
        0
    )

    gray = np.clip(
        gray,
        0,
        255
    ).astype(np.uint8)

    # ----------------------------------------
    # White background
    # ----------------------------------------

    mask = (
        alpha_crop.astype(np.float32) / 255.0
    )

    mask = cv2.GaussianBlur(
        mask,
        (0, 0),
        1
    )

    result = (
        gray.astype(np.float32) * mask
        + 255 * (1 - mask)
    )

    result = np.clip(
        result,
        0,
        255
    ).astype(np.uint8)

    # ----------------------------------------
    # Add padding safely
    # ----------------------------------------

    h, w = result.shape

    padding_x = int(w * 0.18)
    padding_y = int(h * 0.12)

    canvas_width = w + padding_x * 2
    canvas_height = h + padding_y * 2

    canvas = np.full(
        (canvas_height, canvas_width),
        255,
        dtype=np.uint8
    )

    canvas[
        padding_y:padding_y + h,
        padding_x:padding_x + w
    ] = result

    # ----------------------------------------
    # Save
    # ----------------------------------------

    Image.fromarray(
        canvas,
        mode="L"
    ).save(output_file)

    print()
    print("SUCCESS!")
    print("Created:", output_file)
    print(
        "Final size:",
        canvas_width,
        "x",
        canvas_height
    )


if __name__ == "__main__":
    prepare_photo(
        INPUT,
        OUTPUT
    )