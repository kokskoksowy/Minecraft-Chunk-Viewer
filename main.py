from colorsys import yiq_to_rgb

import anvil
import os

def print_chunk_info(region_file_path):
    """
    Prints information about all chunks within a given Minecraft region file.

    Args:
        region_file_path: The path to the Minecraft region file (.mca).
    """
    region = anvil.Region.from_file(region_file_path)

    print(f"Region File: {region_file_path}")

    for x in range(32):
        for z in range(32):

            try:
                chunk = anvil.Chunk.from_region(region, x, z)
                print(f"  Chunk at ({x}, {z})")
            except Exception as e:
                print()





if __name__ == "__main__":
    region_file = r"C:\SERWERMINECRAFT_GRANIE,zapto.org\world\region\r.-12.-37.mca"  # Replace with your region file path
    print_chunk_info(region_file)