import requests
from bs4 import BeautifulSoup
import os
import urllib.parse
import time
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdsWorldScraper:
    def __init__(self, base_url="https://www.adsoftheworld.com", download_dir="downloaded_images"):
        self.base_url = base_url
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        
        # Session for connection pooling and maintaining cookies
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        self.downloaded_count = 0
        self.failed_count = 0
        
    def get_page_content(self, page_num):
        """Get the HTML content of a specific page"""
        try:
            # Use the correct URL structure for adsoftheworld.com
            url = f"{self.base_url}/blog/feed?page={page_num}"
            
            logger.info(f"Fetching page {page_num}: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching page {page_num}: {e}")
            return None
    
    def extract_image_urls(self, html_content):
        """Extract all image URLs from the HTML content"""
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        image_urls = []
        
        # Find all img tags
        img_tags = soup.find_all('img')
        
        for img in img_tags:
            # Get src or data-src attributes
            src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            
            if src:
                # Convert relative URLs to absolute URLs
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    src = self.base_url + src
                elif not src.startswith('http'):
                    src = urllib.parse.urljoin(self.base_url, src)
                
                # Skip very small images (likely icons or thumbnails)
                if any(skip_pattern in src.lower() for skip_pattern in ['icon', 'logo', 'avatar', 'placeholder']):
                    continue
                    
                image_urls.append(src)
        
        return list(set(image_urls))  # Remove duplicates
    
    def download_image(self, image_url, page_num):
        """Download a single image"""
        try:
            # Get filename from URL
            parsed_url = urllib.parse.urlparse(image_url)
            filename = os.path.basename(parsed_url.path)
            
            # If no filename extension, add .jpg as default
            if '.' not in filename or len(filename) < 5:
                filename = f"image_{self.downloaded_count + 1}.jpg"
            
            # Create page-specific directory
            page_dir = self.download_dir / f"page_{page_num}"
            page_dir.mkdir(exist_ok=True)
            
            file_path = page_dir / filename
            
            # Skip if file already exists
            if file_path.exists():
                logger.info(f"Skipping existing file: {filename}")
                return True
            
            # Download image
            response = self.session.get(image_url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Check if it's actually an image
            content_type = response.headers.get('content-type', '').lower()
            if not content_type.startswith('image/'):
                logger.warning(f"Skipping non-image content: {image_url}")
                return False
            
            # Save image
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.downloaded_count += 1
            logger.info(f"Downloaded: {filename} (Total: {self.downloaded_count})")
            return True
            
        except Exception as e:
            self.failed_count += 1
            logger.error(f"Failed to download {image_url}: {e}")
            return False
    
    def detect_pagination_structure(self):
        """Detect the actual pagination structure of the website"""
        logger.info("Detecting pagination structure...")
        
        # Get first page
        html_content = self.get_page_content(1)
        if not html_content:
            return None
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for pagination links
        pagination_patterns = [
            'a[href*="page/"]',
            'a[href*="?page="]', 
            'a[href*="&page="]',
            '.pagination a',
            '.pager a',
            'a:contains("Next")',
            'a:contains(">")',
            '[data-page]'
        ]
        
        for pattern in pagination_patterns:
            links = soup.select(pattern)
            if links:
                logger.info(f"Found pagination with pattern: {pattern}")
                for link in links[:5]:  # Check first 5 links
                    href = link.get('href')
                    if href:
                        logger.info(f"Pagination link found: {href}")
                        return pattern
        
        # Check for infinite scroll indicators
        infinite_scroll_patterns = [
            '[data-infinite-scroll]',
            '.infinite-scroll',
            '[data-load-more]',
            '.load-more'
        ]
        
        for pattern in infinite_scroll_patterns:
            elements = soup.select(pattern)
            if elements:
                logger.info(f"Detected infinite scroll with pattern: {pattern}")
                return "infinite_scroll"
        
        logger.warning("No pagination structure detected")
        return None
    
    def find_actual_page_count(self):
        """Find the actual number of pages available"""
        logger.info("Finding actual page count...")
        
        # Start with a reasonable estimate
        max_page = 1400
        min_page = 1
        
        # Binary search to find the actual last page
        while min_page < max_page:
            mid_page = (min_page + max_page + 1) // 2
            html_content = self.get_page_content(mid_page)
            
            if html_content and self.extract_image_urls(html_content):
                min_page = mid_page
            else:
                max_page = mid_page - 1
        
        logger.info(f"Found actual page count: {min_page}")
        return min_page
    
    def scrape_page(self, page_num):
        """Scrape a single page and download its images"""
        html_content = self.get_page_content(page_num)
        if not html_content:
            return 0
        
        image_urls = self.extract_image_urls(html_content)
        logger.info(f"Found {len(image_urls)} images on page {page_num}")
        
        downloaded = 0
        for image_url in image_urls:
            if self.download_image(image_url, page_num):
                downloaded += 1
            
            # Small delay to be respectful to the server
            time.sleep(0.5)
        
        return downloaded
    
    def scrape_all_pages(self, start_page=1, end_page=1400):
        """Scrape all pages from start_page to end_page"""
        logger.info(f"Starting to scrape pages {start_page} to {end_page}")
        
        for page_num in range(start_page, end_page + 1):
            try:
                downloaded = self.scrape_page(page_num)
                logger.info(f"Page {page_num} completed. Downloaded {downloaded} images.")
                
                # Longer delay between pages
                time.sleep(2)
                
                # Log progress every 50 pages
                if page_num % 50 == 0:
                    logger.info(f"Progress: {page_num}/{end_page} pages completed. "
                              f"Total downloaded: {self.downloaded_count}, Failed: {self.failed_count}")
                
            except KeyboardInterrupt:
                logger.info("Scraping interrupted by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error on page {page_num}: {e}")
                continue
        
        logger.info(f"Scraping completed! Total downloaded: {self.downloaded_count}, Failed: {self.failed_count}")

def main():
    # Create scraper instance
    scraper = AdsWorldScraper()
    
    print(f"Starting image scraper for adsoftheworld.com/blog/feed")
    print(f"Download directory: {scraper.download_dir}")
    print("Press Ctrl+C to stop scraping at any time\n")
    
    # Find the actual number of pages
    max_pages = scraper.find_actual_page_count()
    
    print(f"Detected maximum pages: {max_pages}")
    
    # Ask user for confirmation or let them specify range
    user_input = input(f"Do you want to scrape pages 1 to {max_pages}? (y/n/custom): ")
    
    if user_input.lower() == 'custom':
        try:
            start_page = int(input("Enter start page: "))
            end_page = int(input("Enter end page: "))
            if start_page < 1 or end_page < start_page:
                print("Invalid page range")
                return
        except ValueError:
            print("Invalid input")
            return
    elif user_input.lower() == 'y':
        start_page = 1
        end_page = max_pages
    else:
        print("Scraping cancelled")
        return
    
    print(f"Scraping pages {start_page} to {end_page}")
    
    try:
        scraper.scrape_all_pages(start_page, end_page)
    except KeyboardInterrupt:
        print("\nScraping stopped by user")
    
    print(f"\nFinal Results:")
    print(f"Images downloaded: {scraper.downloaded_count}")
    print(f"Downloads failed: {scraper.failed_count}")
    print(f"Images saved to: {scraper.download_dir}")

if __name__ == "__main__":
    main()