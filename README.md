
# Image Generator Project

This repository provides a complete pipeline for collecting advertisement images from the web and training deep learning models to generate or denoise images. It includes:

1. **Image Scraper** (`image_scraaperr.py`): Scrapes images from [Ads of the World](https://www.adsoftheworld.com) and organizes them by page.
2. **Image Generator (GAN)** (`iteration2.ipynb`, `tensor-gan (1).ipynb`): Jupyter notebooks for training Generative Adversarial Networks (GANs) using PyTorch or TensorFlow.

---

## Table of Contents
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
  - [Image Scraper](#image-scraper)
  - [GAN Training (PyTorch)](#gan-training-pytorch)
  - [GAN Training (TensorFlow)](#gan-training-tensorflow)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)
- [Requirements](#requirements)
- [License](#license)

---

## Features
- Scrape images from hundreds of pages with robust error handling
- Organize images by page for easy dataset management
- Train GANs for image generation and denoising (PyTorch and TensorFlow examples)
- Visualize training progress and generated images
- Easily customize dataset paths, model parameters, and output directories

---

## Project Structure

- `image_scraaperr.py` — Scrapes images from Ads of the World, supports pagination, duplicate removal, and error logging
- `iteration2.ipynb` — PyTorch GAN for denoising and generating images, includes training loop and visualization
- `tensor-gan (1).ipynb` — TensorFlow DCGAN for custom datasets, with configuration class and output management
- `requirements.txt` — Python dependencies for all scripts and notebooks
- `training_curves.png` — Example of GAN training progress
- `*.png` — Generated or downloaded images

---

## Installation

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd image_generator
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   For TensorFlow notebook, you may need:
   ```bash
   pip install tensorflow matplotlib imageio
   ```

---

## Usage

### Image Scraper
Run the scraper to download images from Ads of the World:
```bash
python image_scraaperr.py
```
You will be prompted to select the page range. Images are saved in `downloaded_images/page_<n>/`.

**Customization:**
- Change `base_url` or `download_dir` in the script to target other sites or folders.
- The script automatically detects pagination and skips icons/logos.

### GAN Training (PyTorch)
**Model Architecture:**
- **Generator:** Encoder-decoder CNN with Conv2d, BatchNorm, ReLU, and ConvTranspose2d layers. Takes noisy images and outputs denoised/generated images (256x256 RGB).
- **Discriminator:** CNN with Conv2d, BatchNorm, LeakyReLU, and Sigmoid layers. Classifies images as real or fake.

**Details:**
- The PyTorch GAN is designed for image denoising and generation. The generator uses an encoder-decoder structure to transform noisy images into clean outputs. The discriminator is a binary classifier that distinguishes real images from those produced by the generator.
- Training uses MSE loss for both generator and discriminator, Adam optimizer, and batch normalization for stable learning. Images are processed at 256x256 resolution.
- Use case: Denoising, image restoration, and basic image generation tasks.

Open `iteration2.ipynb` in Jupyter or VS Code. The notebook:
- Loads images from `dataset/train` and `dataset/test` (use your scraped images)
- Defines Generator and Discriminator models
- Trains for 100 epochs, saving generated images to `outputs/`
- Visualizes training curves and sample outputs

**Customization:**
- Adjust model architecture, batch size, or epochs in the notebook
- Change dataset paths to use your own images

### GAN Training (TensorFlow)
**Model Architecture:**
- **Generator:** Deep CNN (DCGAN) with Dense, BatchNorm, LeakyReLU, and multiple Conv2DTranspose layers. Upsamples random noise to generate high-resolution images (e.g., 64x64 RGB).
- **Discriminator:** Deep CNN with Conv2D, BatchNorm, LeakyReLU, and Dense layers. Distinguishes real from generated images.

**Details:**
- The TensorFlow DCGAN is optimized for generating realistic images from random noise vectors. The generator starts with a dense layer and progressively upsamples using Conv2DTranspose layers, batch normalization, and LeakyReLU activations. The discriminator uses convolutional layers to classify images as real or fake.
- Training uses binary cross-entropy loss, Adam optimizer, and supports flexible image sizes and dataset formats. Output images are typically 64x64 RGB, but can be customized.
- Use case: Synthetic image generation, creative content, and dataset augmentation.

---

## Model Comparison

| Feature                | PyTorch GAN (iteration2.ipynb)         | TensorFlow DCGAN (tensor-gan (1).ipynb) |
|------------------------|----------------------------------------|-----------------------------------------|
| Framework              | PyTorch                                | TensorFlow                              |
| Generator Input        | Noisy real images                      | Random noise vector                     |
| Generator Output       | Denoised/generated images (256x256)    | Generated images (64x64, customizable)  |
| Generator Structure    | Encoder-decoder CNN                    | Deep CNN with Conv2DTranspose           |
| Discriminator Input    | Real or generated images               | Real or generated images                |
| Discriminator Output   | Real/Fake (binary)                     | Real/Fake (binary)                      |
| Loss Function          | MSE                                    | Binary Cross-Entropy                    |
| Optimizer              | Adam                                   | Adam                                    |
| Dataset Format         | Folder with train/test images          | Folder with images (customizable)       |
| Customization          | Easy to change model, data paths       | Config class for all parameters         |
| Use Case               | Denoising, restoration, basic gen      | Synthetic image generation              |
| Output Directory       | outputs/                               | dcgan_output/, training_checkpoints/    |

---

Open `tensor-gan (1).ipynb` for DCGAN training:
- Uses a configuration class for easy parameter changes
- Loads images from a specified dataset path
- Trains and saves checkpoints, logs, and generated images

**Customization:**
- Edit the `Config` class to change dataset location, image size, batch size, etc.
- Supports multiple image formats (JPG, PNG, BMP, TIFF)

---

## Troubleshooting
- If scraping fails, check your internet connection and site accessibility
- For large downloads, ensure enough disk space
- For GAN training, verify dataset structure matches notebook expectations
- For TensorFlow, install missing packages as needed

---

## Requirements
See `requirements.txt` for core dependencies:
- torch
- torchvision
- pillow
- requests
- beautifulsoup4
- numpy

TensorFlow notebook also requires:
- tensorflow
- matplotlib
- imageio

---

## License
This project is licensed under the MIT License.
