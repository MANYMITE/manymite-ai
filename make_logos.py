"""Generate the Sathvik AI logo set with PIL (runs INSIDE the open-webui
container, which has Pillow). Outputs to /tmp/sathvik_static/.
"""
import os
from PIL import Image, ImageDraw

OUT = "/tmp/sathvik_static"
os.makedirs(OUT, exist_ok=True)

C1 = (108, 140, 255)   # #6c8cff
C2 = (154, 108, 255)   # #9a6cff
WHITE = (255, 255, 255, 255)

# lightning bolt polygon on a 100x100 viewbox
BOLT = [(57, 4), (26, 54), (45, 54), (38, 96), (74, 40), (52, 40), (66, 4)]


def rounded_gradient(size):
    """Return an RGBA image: rounded-square badge with a diagonal gradient."""
    s4 = size * 4  # supersample for smooth edges
    img = Image.new("RGBA", (s4, s4), (0, 0, 0, 0))
    grad = Image.new("RGBA", (s4, s4))
    px = grad.load()
    for y in range(s4):
        for x in range(s4):
            t = (x + y) / (2 * s4)
            r = int(C1[0] + (C2[0] - C1[0]) * t)
            g = int(C1[1] + (C2[1] - C1[1]) * t)
            b = int(C1[2] + (C2[2] - C1[2]) * t)
            px[x, y] = (r, g, b, 255)
    mask = Image.new("L", (s4, s4), 0)
    d = ImageDraw.Draw(mask)
    rad = int(s4 * 0.24)
    d.rounded_rectangle([0, 0, s4 - 1, s4 - 1], radius=rad, fill=255)
    img.paste(grad, (0, 0), mask)
    # bolt, scaled up with the supersample
    scale = s4 / 100.0
    bolt = [(int(x * scale), int(y * scale)) for x, y in BOLT]
    bd = ImageDraw.Draw(img)
    bd.polygon(bolt, fill=WHITE)
    return img.resize((size, size), Image.LANCZOS)


def save(name, img):
    p = os.path.join(OUT, name)
    if name.endswith(".ico"):
        img.save(p, format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])
    else:
        img.save(p)
    print("wrote", p)


# full set, mirroring Open WebUI's static files
save("logo.png", rounded_gradient(512))
save("logo-dark.png", rounded_gradient(512))
save("favicon.png", rounded_gradient(256))
save("favicon-96x96.png", rounded_gradient(96))
save("apple-touch-icon.png", rounded_gradient(180))
save("web-app-manifest-192x192.png", rounded_gradient(192))
save("web-app-manifest-512x512.png", rounded_gradient(512))
save("favicon.ico", rounded_gradient(48))

# splash: dark 1080x1080 with centered badge
sp = Image.new("RGB", (1080, 1080), (11, 15, 26))
badge = rounded_gradient(360)
sp.paste(badge, (360, 360), badge)
sp.save(os.path.join(OUT, "splash.png"))
sp.save(os.path.join(OUT, "splash-dark.png"))
print("wrote splash.png / splash-dark.png")

# svg favicon (crisp vector version)
svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#6c8cff"/><stop offset="1" stop-color="#9a6cff"/>
</linearGradient></defs>
<rect width="100" height="100" rx="24" fill="url(#g)"/>
<polygon points="57,4 26,54 45,54 38,96 74,40 52,40 66,4" fill="#fff"/>
</svg>"""
with open(os.path.join(OUT, "favicon.svg"), "w") as f:
    f.write(svg)
print("wrote favicon.svg")
