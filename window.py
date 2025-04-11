import random
from PIL import Image, ImageFilter, ImageTk
import os
import math
import tkinter as tk

CLOUD_SCALE = 2

DEFAULT_WIDTH = 2400
DEFAULT_HEIGHT = 3200
SCALE_FACTOR = 6

def get_unique_filename(base_name="cloud", extension="png", folder="clouds"):
    os.makedirs(folder, exist_ok=True)
    counter = 1
    while True:
        filename = f"{base_name}{counter}.{extension}"
        full_path = os.path.join(folder, filename)
        if not os.path.exists(full_path):
            return full_path
        counter += 1

def create_low_res_gradient(width, height):
    img = Image.new("RGB", (width, height))
    pixels = img.load()

    top_sky = (70, 130, 180)
    mid_sky = (173, 216, 230)
    horizon_sky = (250, 250, 250)

    horizon_line = int(height * 0.80)
    fog_line = height

    for y in range(height):
        if y < horizon_line:
            blend = y / horizon_line
            r = int(top_sky[0] * (1 - blend) + mid_sky[0] * blend)
            g = int(top_sky[1] * (1 - blend) + mid_sky[1] * blend)
            b = int(top_sky[2] * (1 - blend) + mid_sky[2] * blend)
        else:
            blend = (y - horizon_line) / (fog_line - horizon_line)
            blend = min(1.0, max(0.0, blend))
            r = int(mid_sky[0] * (1 - blend) + horizon_sky[0] * blend)
            g = int(mid_sky[1] * (1 - blend) + horizon_sky[1] * blend)
            b = int(mid_sky[2] * (1 - blend) + horizon_sky[2] * blend)

        for x in range(width):
            pixels[x, y] = (r, g, b)

    return img

def add_wispy_clouds(img, clusters, base_color, opacity_multiplier=1.0):
    wind_strength = 0.3
    warp_strength = 0.5

    pixels = img.load()
    w, h = img.size
    r_base, g_base, b_base = base_color

    for (cx, cy, cluster_radius, sublumps, max_radius) in clusters:
        cluster_radius = int(cluster_radius * CLOUD_SCALE)
        sublumps = int(sublumps * CLOUD_SCALE)
        max_radius = int(max_radius * CLOUD_SCALE)

        for _ in range(sublumps):
            alpha_base = random.uniform(0.6, 1.0)
            spread_x = random.randint(-cluster_radius // 2, cluster_radius // 2)
            spread_y = random.randint(-cluster_radius // 2, cluster_radius // 2)

            sub_cx = cx + spread_x
            sub_cy = cy + spread_y
            r_sublump = random.randint(max_radius // 2, max_radius)

            x_min = max(0, sub_cx - r_sublump)
            x_max = min(w, sub_cx + r_sublump)
            y_min = max(0, sub_cy - r_sublump)
            y_max = min(h, sub_cy + r_sublump)

            for x in range(x_min, x_max):
                for y in range(y_min, y_max):
                    dx = x - sub_cx
                    dy = y - sub_cy
                    dist = (dx**2 + dy**2) ** 0.5

                    if dist <= r_sublump:
                        normalized_dist = dist / r_sublump
                        feather = 0.5 * (1 + math.cos(normalized_dist * math.pi))
                        feather = max(0, min(1, feather))

                        brightness = feather
                        brightness = max(0.2, min(1, brightness))

                        r_old, g_old, b_old = pixels[x, y]
                        alpha = brightness * 0.6 * opacity_multiplier

                        r = int(r_base * alpha + r_old * (1 - alpha))
                        g = int(g_base * alpha + g_old * (1 - alpha))
                        b = int(b_base * alpha + b_old * (1 - alpha))

                        pixels[x, y] = (r, g, b)

def generate_cloud_image(final_width, final_height, scale_factor):
    low_width = final_width // scale_factor
    low_height = final_height // scale_factor

    cloud_color = (255, 255, 245)
    low_res_img = create_low_res_gradient(low_width, low_height)

    clusters = [
        (int(low_width * 0.15), int(low_height * 0.10), 16, 14, 9),
        (int(low_width * 0.30), int(low_height * 0.20), 20, 18, 10),
        (int(low_width * 0.70), int(low_height * 0.18), 18, 16, 9),
        (int(low_width * 0.85), int(low_height * 0.25), 24, 22, 12),
        (int(low_width * 0.10), int(low_height * 0.40), 14, 12, 8),
        (int(low_width * 0.50), int(low_height * 0.30), 22, 20, 11),
        (int(low_width * 0.30), int(low_height * 0.60), 20, 18, 10),
        (int(low_width * 0.85), int(low_height * 0.50), 25, 22, 13),
        (int(low_width * 0.60), int(low_height * 0.65), 18, 15, 9),
        (int(low_width * 0.35), int(low_height * 0.80), 26, 24, 14),
        (int(low_width * 0.75), int(low_height * 0.75), 22, 20, 11),
        (int(low_width * 0.50), int(low_height * 0.90), 28, 26, 15),
        (int(low_width * 0.95), int(low_height * 0.85), 16, 14, 9),
        (int(low_width * 0.20), int(low_height * 0.95), 25, 23, 12),
    ]

    add_wispy_clouds(low_res_img, clusters, cloud_color, opacity_multiplier=0.4)
    add_wispy_clouds(low_res_img, clusters, cloud_color, opacity_multiplier=1.0)

    final_img = low_res_img.resize((final_width, final_height), Image.BICUBIC)
    final_img = final_img.filter(ImageFilter.GaussianBlur(radius=0.2))

    return final_img

def main():
    final_width, final_height = DEFAULT_WIDTH, DEFAULT_HEIGHT
    scale_factor = SCALE_FACTOR

    # Generate the cloud image first
    final_img = generate_cloud_image(final_width, final_height, scale_factor)

    # Create Tkinter window with exact size of the image
    window = tk.Tk()
    window.title("clouds :o")
    window.geometry(f"{final_width}x{final_height}")
    window.configure(background='black')

    # Convert PIL image to Tkinter-compatible image
    tk_img = ImageTk.PhotoImage(final_img)
    label = tk.Label(window, image=tk_img)
    label.image = tk_img  # prevent garbage collection
    label.pack()

    window.mainloop()

if __name__ == "__main__":
    main()
