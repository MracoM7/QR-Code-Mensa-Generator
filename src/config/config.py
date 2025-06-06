"""Configurazioni centrali per il QR Code Mensa Generator"""

# Configurazioni QR Code
QR_CONFIG = {
    "version": 1,
    "error_correction": "M",  # L, M, Q, H
    "box_size": 10,
    "border": 4,
    "fill_color": "black",
    "back_color": "white"
}

# Configurazioni Output
OUTPUT_CONFIG = {
    "format": "PNG",
    "quality": 95,
    "default_filename": "mensa.png"
}

# Headers per requests
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}