"""
Advanced image preprocessing utilities for OCR quality improvement.

The core preprocessing pipeline lives in ``OCRService._preprocess_image()``.
This module provides supplementary helpers for edge cases encountered in
scanned Indian legal documents (border shadows, skew, low contrast).

All functions accept and return NumPy arrays in the same colour space as
the input (grayscale in, grayscale out; BGR in, BGR out).
"""

from __future__ import annotations

import logging

import cv2
import numpy as np

logger = logging.getLogger(__name__)


def deskew_image(image: np.ndarray) -> np.ndarray:
    """
    Correct document skew using the Hough Line Transform.

    Detects the dominant text orientation and rotates the image to
    straighten lines.  Skew angles below 0.5° are ignored to avoid
    unnecessary resampling.

    Args:
        image: BGR or grayscale image array.

    Returns:
        Deskewed image (same colour space as input).
    """
    gray = (
        cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if len(image.shape) == 3
        else image
    )

    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

    if lines is None:
        return image

    angles: list[float] = []
    for line in lines[:10]:  # Sample top 10 lines for speed
        _rho, theta = line[0]
        angle = (theta * 180.0 / np.pi) - 90.0
        angles.append(angle)

    if not angles:
        return image

    median_angle = float(np.median(angles))

    if abs(median_angle) <= 0.5:
        logger.debug("Skew angle %.2f° below threshold — skipping deskew.", median_angle)
        return image

    logger.debug("Deskewing image by %.2f°.", median_angle)
    center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(center, median_angle, 1.0)
    rotated = cv2.warpAffine(
        image,
        rot_mat,
        image.shape[1::-1],
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE,
    )
    return rotated


def remove_borders(image: np.ndarray) -> np.ndarray:
    """
    Crop away dark scanner borders from a scanned document image.

    Finds the largest bright contour (document content area) and returns
    just that region, removing any black shadow borders introduced by
    flatbed scanners.

    Args:
        image: BGR or grayscale image array.

    Returns:
        Cropped image with borders removed.  Returns the original image
        unchanged if no contour can be found.
    """
    gray = (
        cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if len(image.shape) == 3
        else image
    )

    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return image

    largest = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest)

    logger.debug("Removing borders: cropping to (%d, %d, %d, %d).", x, y, w, h)
    return image[y : y + h, x : x + w]


def enhance_resolution(image: np.ndarray, scale: float = 2.0) -> np.ndarray:
    """
    Upscale a low-resolution image for better OCR accuracy.

    Simple bicubic upscaling.  For very low-DPI scans (< 150 DPI), this
    can substantially improve PaddleOCR recognition rates.

    Args:
        image: BGR or grayscale image array.
        scale: Upscale factor (default 2×).

    Returns:
        Upscaled image.
    """
    if scale <= 1.0:
        return image

    h, w = image.shape[:2]
    new_w = int(w * scale)
    new_h = int(h * scale)
    logger.debug("Upscaling image %dx%d → %dx%d.", w, h, new_w, new_h)
    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_CUBIC)


def binarize_sauvola(image: np.ndarray, window_size: int = 25) -> np.ndarray:
    """
    Apply Sauvola local thresholding — an alternative to Gaussian adaptive
    thresholding that performs better on documents with uneven illumination.

    Sauvola's formula:  T(x,y) = μ(x,y) * [1 + k * (σ(x,y)/R - 1)]
    where k=0.2, R=128 (half dynamic range).

    Args:
        image:       Grayscale image array.
        window_size: Local neighbourhood size (must be odd).

    Returns:
        Binary image (0/255 values).
    """
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    k = 0.2
    R = 128.0

    # Compute local mean and standard deviation via integral images
    image_f = image.astype(np.float64)
    mean = cv2.boxFilter(image_f, -1, (window_size, window_size))
    sq_mean = cv2.boxFilter(image_f ** 2, -1, (window_size, window_size))
    std = np.sqrt(np.maximum(sq_mean - mean ** 2, 0))

    threshold = mean * (1.0 + k * (std / R - 1.0))
    binary = np.where(image_f >= threshold, 255, 0).astype(np.uint8)
    return binary
