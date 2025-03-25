import random
from PIL import Image
import os
import math

CLOUD_SCALE = 2


def get_unique_filename(base_name="cloud", extension="png"):
    counter = 1
    while True:
        filename = f"{base_name}{counter}.{extension}"
        if not os.path.exists(filename):
            return filename
        counter += 1

def create_low_res_gradient(width, height, top_color, bottom_color):
    img = Image.new("RGB", (width, height))
    pixels = img.load()
    
    for y in range(height):
        t = y / (height - 1)
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
        for x in range(width):
            pixels[x, y] = (r, g, b)
    
    return img

def add_wispy_clouds(img, clusters, base_color):
    pixels = img.load()
    w, h = img.size
    r_base, g_base, b_base = base_color

    shading_map = {}

    for (cx, cy, cluster_radius, sublumps, max_radius) in clusters:
        cluster_radius = int(cluster_radius * CLOUD_SCALE)
        sublumps = int(sublumps * CLOUD_SCALE)
        max_radius = int(max_radius * CLOUD_SCALE)

        for _ in range(sublumps):
            alpha_base = random.uniform(0.4, 0.8)
            spread_x = random.randint(-cluster_radius, cluster_radius)
            spread_y = random.randint(-cluster_radius, cluster_radius)

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

                        r_old, g_old, b_old = pixels[x, y]
                        alpha = feather * 0.6  

                        r = int(r_base * alpha + r_old * (1 - alpha))
                        g = int(g_base * alpha + g_old * (1 - alpha))
                        b = int(b_base * alpha + b_old * (1 - alpha))

                        pixels[x, y] = (r, g, b)


def main():
    final_width, final_height = 2400, 3200
    scale_factor = 6 

    low_width = final_width // scale_factor
    low_height = final_height // scale_factor

    top_sky = (173, 216, 230)  
    bottom_sky = (240, 240, 240)  
    cloud_color = (255, 255, 255)  
    
    low_res_img = create_low_res_gradient(low_width, low_height, top_sky, bottom_sky)
    
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
    
    add_wispy_clouds(low_res_img, clusters, cloud_color)
    
    final_img = low_res_img.resize((final_width, final_height), Image.NEAREST)
    
    filename = get_unique_filename("cloud", "png")
    final_img.save(filename)
    print(f"Saved image as {filename}")
    final_img.show()

if __name__ == "__main__":
    main()
