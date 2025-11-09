#!/usr/bin/env python3
"""
Fullscreen Message Display with Flashing Intro
Auto-installs dependencies on first run
"""

import subprocess
import sys
import time
import os

# Hide console window on Windows
if sys.platform == 'win32':
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# === AUTO-INSTALL DEPENDENCIES ===
def install_dependencies():
    """Auto-install required packages"""
    required_packages = ['pygame', 'requests', 'pillow']
    
    print("Checking dependencies...")
    for package in required_packages:
        try:
            __import__(package.replace('pillow', 'PIL'))
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])
    print("Dependencies ready!\n")

install_dependencies()

# Now import the packages
import pygame
import requests
from PIL import Image
from io import BytesIO

# === CONFIGURATION ===
MSG_TEXT = "Who Is This Black Boy ? Isn't He Asit Diwedi ? Am I Right Aniket, Kartik, Adyant and Deeeeeeptanshu Shukla ?"
TEXT_COLOR = (0, 0, 0)  # Black
BG_COLOR = (255, 255, 255)  # White
FONT_TYPE = "segoeui"  # Segoe UI
FONT_SIZE = 64

IMAGE_URL = "https://raw.githubusercontent.com/rohan6379/Server/refs/heads/main/Diwedi.jpg"
IMAGE_WIDTH = 300
# ======================

def flash_screen(duration=5):
    """Flash red and blue colors for specified duration"""
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Loading...")
    
    clock = pygame.time.Clock()
    start_time = time.time()
    
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    
    while time.time() - start_time < duration:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
        
        # Alternate between red and blue every 0.5 seconds
        elapsed = time.time() - start_time
        if int(elapsed * 2) % 2 == 0:
            screen.fill(RED)
        else:
            screen.fill(BLUE)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

def download_image(url):
    """Download image from URL and return pygame surface"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Load image with PIL
        pil_image = Image.open(BytesIO(response.content))
        
        # Resize to specified width while maintaining aspect ratio
        aspect_ratio = pil_image.height / pil_image.width
        new_height = int(IMAGE_WIDTH * aspect_ratio)
        pil_image = pil_image.resize((IMAGE_WIDTH, new_height), Image.Resampling.LANCZOS)
        
        # Convert to pygame surface
        mode = pil_image.mode
        size = pil_image.size
        data = pil_image.tobytes()
        
        return pygame.image.fromstring(data, size, mode)
    except Exception as e:
        print(f"Could not load image: {e}")
        return None

def wrap_text(text, font, max_width):
    """Wrap text to fit within max_width"""
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                lines.append(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

def show_message():
    """Display fullscreen message with image"""
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Message")
    
    screen_width, screen_height = screen.get_size()
    
    # Load font
    try:
        font = pygame.font.SysFont(FONT_TYPE, FONT_SIZE)
    except:
        font = pygame.font.Font(None, FONT_SIZE)
    
    # Download and prepare image
    image_surface = download_image(IMAGE_URL) if IMAGE_URL else None
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                running = False
        
        # Fill background
        screen.fill(BG_COLOR)
        
        # Calculate positions
        y_offset = screen_height // 3
        
        # Draw image if available
        if image_surface:
            image_rect = image_surface.get_rect(center=(screen_width // 2, y_offset))
            screen.blit(image_surface, image_rect)
            y_offset = image_rect.bottom + 40
        
        # Wrap and render text
        max_text_width = screen_width - 100
        lines = wrap_text(MSG_TEXT, font, max_text_width)
        
        line_height = font.get_linesize()
        total_text_height = len(lines) * line_height
        
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, TEXT_COLOR)
            text_rect = text_surface.get_rect(center=(screen_width // 2, y_offset + i * line_height))
            screen.blit(text_surface, text_rect)
        
        pygame.display.flip()
    
    pygame.quit()

def main():
    """Main execution"""
    try:
        # Show flashing screen for 5 seconds
        flash_screen(5)
        
        # Reinitialize pygame and show main content
        show_message()
    except KeyboardInterrupt:
        print("\nExiting...")
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
