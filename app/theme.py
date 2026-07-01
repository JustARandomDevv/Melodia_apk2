"""
Jetons de design Melodia — un noir profond légèrement vert, un accent
émeraude signature, et des cartes "verre" en superposition (glassmorphism
approximé : Kivy ne supporte pas le vrai backdrop-blur, on simule avec des
couches semi-transparentes + une bordure lumineuse fine).
"""

# Fond
BG_TOP = (0.027, 0.039, 0.055, 1)      # #070a0e
BG_BOTTOM = (0.043, 0.094, 0.055, 1)   # #0b180e

# Surfaces "verre"
GLASS = (1, 1, 1, 0.055)
GLASS_BORDER = (1, 1, 1, 0.14)
GLASS_HI = (1, 1, 1, 0.09)

# Accent signature
ACCENT = (0.188, 0.820, 0.345, 1)      # #30d158
ACCENT_DIM = (0.188, 0.820, 0.345, 0.35)

# Texte
TEXT_PRIMARY = (1, 1, 1, 0.95)
TEXT_SECONDARY = (1, 1, 1, 0.55)
TEXT_TERTIARY = (1, 1, 1, 0.30)

RADIUS_LG = 22
RADIUS_MD = 16
RADIUS_SM = 10
