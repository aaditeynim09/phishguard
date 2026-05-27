from PIL import Image, ImageDraw

def create_icon(size, filename):
    img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # Shield shape (simple but clean)
    draw.polygon([
        (size * 0.5, size * 0.05),
        (size * 0.9, size * 0.25),
        (size * 0.8, size * 0.85),
        (size * 0.5, size * 0.98),
        (size * 0.2, size * 0.85),
        (size * 0.1, size * 0.25),
    ], fill=(0, 120, 255, 255))

    img.save(filename)
    print(f"Created {filename}")

# Generate icons in 3 sizes
create_icon(16, "icon16.png")
create_icon(48, "icon48.png")
create_icon(128, "icon128.png")

print("All icons generated successfully!")
