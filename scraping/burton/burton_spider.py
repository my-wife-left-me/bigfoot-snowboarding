"""
Burton Snowboards Scraper

This scraper uses Selenium for both catalog loading and individual product scraping
because Burton's pages are heavily JavaScript-rendered.

The output follows the standardized schema defined in standard_schema.py
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime
import time
import json
from pathlib import Path
import sys
import os
import re

# Add parent directory to path to import standard_schema
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from standard_schema import ScraperOutput, Board, SizeChart


class BurtonScraper:
    """
    Complete Burton scraper using Selenium for everything.
    """

    # DEBUG MODE: Set to True to only scrape one board
    DEBUG_MODE = False

    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
        self.scraped_boards = []

    def setup_driver(self):
        """Initialize Selenium WebDriver"""
        options = webdriver.FirefoxOptions()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")
        options.set_preference(
            "general.useragent.override",
            "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
        )

        self.driver = webdriver.Firefox(options=options)
        # Reduce implicit wait to avoid slowdowns
        self.driver.implicitly_wait(2)

    def get_product_urls_and_images(self, catalog_url):
        """
        Load the catalog page and extract all product URLs and images.
        Does NOT visit individual product pages.
        """
        print("=" * 60)
        print("PHASE 1: Loading catalog with Selenium")
        print("=" * 60)

        print(f"Loading catalog page: {catalog_url}")
        self.driver.get(catalog_url)

        # Wait for initial products to load
        wait = WebDriverWait(self.driver, 15)
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "article.product-card"))
        )

        # Handle cookie consent banner if present
        try:
            time.sleep(2)
            banner = self.driver.find_element(By.ID, "onetrust-banner-sdk")
            if banner.is_displayed():
                accept_btn = self.driver.find_element(
                    By.ID, "onetrust-accept-btn-handler"
                )
                accept_btn.click()
                print("✓ Dismissed cookie consent banner")
                time.sleep(2)
        except NoSuchElementException:
            pass

        # Count initial products
        initial_count = len(
            self.driver.find_elements(By.CSS_SELECTOR, "article.product-card")
        )
        print(f"Initial products loaded: {initial_count}")

        # Scroll to bottom
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # Click "Load More" button until all products are loaded
        load_more_clicks = 0
        max_clicks = 10

        while load_more_clicks < max_clicks:
            try:
                time.sleep(2)

                # Find "Load More" button
                load_more_button = self.driver.find_element(
                    By.CSS_SELECTOR, "a.load-more-button"
                )
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                    load_more_button,
                )
                time.sleep(2)

                if not load_more_button.is_displayed():
                    break

                before_count = len(
                    self.driver.find_elements(By.CSS_SELECTOR, "article.product-card")
                )

                try:
                    load_more_button.click()
                except Exception:
                    self.driver.execute_script(
                        "arguments[0].click();", load_more_button
                    )

                load_more_clicks += 1
                print(f"Clicked 'Load More' ({load_more_clicks} times)")

                time.sleep(4)
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
                time.sleep(1)

                current_count = len(
                    self.driver.find_elements(By.CSS_SELECTOR, "article.product-card")
                )
                print(f"Products: {before_count} → {current_count}")

                if current_count == before_count:
                    break

            except NoSuchElementException:
                break

        # Extract product links and images from the catalog page only
        print(f"\nExtracting URLs and images from catalog page...")
        start_time = time.time()

        try:
            product_cards = self.driver.find_elements(
                By.CSS_SELECTOR, "article.product-card"
            )
            print(
                f"Found {len(product_cards)} product cards (took {time.time() - start_time:.2f}s)"
            )
        except Exception as e:
            print(f"Error finding product cards: {e}")
            return []

        # Temporarily disable implicit wait for faster extraction
        self.driver.implicitly_wait(0)

        product_data = []

        for idx, card in enumerate(product_cards, 1):
            try:
                # Get URL
                links = card.find_elements(
                    By.CSS_SELECTOR, "a.product-card__image-wrap"
                )
                if not links:
                    continue
                url = links[0].get_attribute("href")

                # Get image URL - try picture source first
                image_url = None
                sources = card.find_elements(By.CSS_SELECTOR, "picture source")
                if sources:
                    srcset = sources[0].get_attribute("srcset")
                    if srcset:
                        image_url = srcset.split(" 1x")[0].strip()

                # Fallback to img tag
                if not image_url:
                    imgs = card.find_elements(By.CSS_SELECTOR, "img")
                    if imgs:
                        image_url = imgs[0].get_attribute("src")

                if url:
                    product_data.append({"url": url, "image_url": image_url})

            except Exception as e:
                print(f"  ⚠ Error on card {idx}: {e}")
                continue

        # Restore implicit wait
        self.driver.implicitly_wait(2)

        elapsed = time.time() - start_time
        print(f"✓ Extracted {len(product_data)} products in {elapsed:.2f}s")
        return product_data

    def scrape_product(self, url, image_url):
        """Scrape a single product page"""
        print(f"\nScraping: {url}")

        self.driver.get(url)

        # Wait for product name to load
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.product-name"))
            )
        except TimeoutException:
            print(f"  ✗ Timeout waiting for product name")
            return None

        # Extract product name
        try:
            product_name = self.driver.find_element(
                By.CSS_SELECTOR, "h1.product-name"
            ).text.strip()
        except NoSuchElementException:
            print(f"  ✗ No product name found")
            return None

        # Extract gender
        gender = self.extract_gender(product_name)

        # Extract model year from URL
        model_year = self.extract_year_from_url(url)

        # Extract price
        price = None
        try:
            price_str = self.driver.find_element(
                By.CSS_SELECTOR, ".product-price .standard-price"
            ).text
            price = self.parse_price(price_str)
        except NoSuchElementException:
            pass

        # Extract tech details
        tech_details = self.parse_tech_details()

        # Extract tech specs
        tech_specs = self.parse_tech_specs_accordion()

        # Extract terrain sliders
        terrain_data = self.parse_terrain_sliders()

        # Extract size chart
        size_chart = self.parse_size_chart()

        # Build board data
        board_data = {
            "name": product_name,
            "url": url,
            "model_year": model_year,
            "gender": gender,
            "price": price,
            "image_url": image_url,
            "profile_type": tech_details.get("profile_type"),
            "profile_description": tech_details.get("profile_description"),
            "shape_type": tech_details.get("shape_type"),
            "shape_description": tech_details.get("shape_description"),
            "ability_levels": tech_specs.get("ability_levels"),
            "terrain_types": terrain_data.get("terrain_types"),
            "flex_rating": terrain_data.get("flex_rating"),
            "response": terrain_data.get("response"),
            "size_chart": size_chart,
        }

        board = Board(**board_data)
        print(f"  ✓ {board.name} ({board.gender}, {model_year})")
        print(f"    Profile: {board.profile_type}, Shape: {board.shape_type}")
        print(f"    Terrain: {board.terrain_types}, Flex: {board.flex_rating}/10")

        return board

    def extract_gender(self, name: str) -> str:
        """Extract gender from product name prefix"""
        if name.startswith("Men's"):
            return "MENS"
        elif name.startswith("Women's"):
            return "WOMENS"
        elif name.startswith("Kid's") or name.startswith("Kids"):
            return "KIDS"
        else:
            return "UNISEX"

    def extract_year_from_url(self, url: str) -> int:
        """Extract year from URL (e.g., W26-106881 -> 2026)"""
        match = re.search(r"W(\d{2})-", url)
        if match:
            year_suffix = match.group(1)
            return 2000 + int(year_suffix)
        return None

    def parse_price(self, price_str: str) -> float:
        """Parse price string to float"""
        if not price_str:
            return None
        try:
            return float(price_str.replace("$", "").replace(",", ""))
        except:
            return None

    def parse_tech_details(self) -> dict:
        """Parse tech detail cards for profile/bend and shape"""
        tech_data = {}

        try:
            tech_cards = self.driver.find_elements(By.CSS_SELECTOR, "div.tech-details")

            for card in tech_cards:
                try:
                    tech_type = (
                        card.find_element(By.CSS_SELECTOR, "h3.tech-type-header")
                        .text.strip()
                        .lower()
                    )
                    tech_name = card.find_element(
                        By.CSS_SELECTOR, "h4.tech-details-name"
                    ).text.strip()
                    tech_desc = card.find_element(
                        By.CSS_SELECTOR, "p.tech-description"
                    ).text.strip()

                    if "bend" in tech_type or "profile" in tech_type:
                        tech_data["profile_type"] = tech_name
                        tech_data["profile_description"] = tech_desc
                    elif "shape" in tech_type:
                        tech_data["shape_type"] = tech_name
                        tech_data["shape_description"] = tech_desc
                except NoSuchElementException:
                    continue
        except:
            pass

        return tech_data

    def parse_tech_specs_accordion(self) -> dict:
        """Parse Tech Specs accordion for ability levels"""
        specs_data = {}

        try:
            # Find the Tech Specs accordion
            accordion = self.driver.find_element(By.CSS_SELECTOR, "div#\\-Tech\\ Specs")

            # Check if it's collapsed (has display: none)
            details = accordion.find_element(
                By.CSS_SELECTOR, "dd.accordion-item-details"
            )
            style = details.get_attribute("style")

            # Click to expand if collapsed
            if "display: none" in style or style == "":
                accordion_button = accordion.find_element(
                    By.CSS_SELECTOR, "button.accordion-item-trigger"
                )
                self.driver.execute_script("arguments[0].click();", accordion_button)
                time.sleep(0.5)

            # Find Riding Level
            list_items = accordion.find_elements(
                By.CSS_SELECTOR, "ul.accordion-item-details-inner-list > li"
            )

            for li in list_items:
                try:
                    # Get the item title text directly from the li
                    item_text = li.text

                    if "Riding Level" in item_text:
                        # Get the nested ul li elements
                        levels = li.find_elements(By.CSS_SELECTOR, "ul li")
                        ability_levels = [
                            level.text.strip() for level in levels if level.text.strip()
                        ]
                        if ability_levels:
                            specs_data["ability_levels"] = ability_levels
                        break
                except:
                    continue
        except Exception as e:
            print(f"    ⚠ Could not parse Tech Specs: {e}")

        return specs_data

    def parse_terrain_sliders(self) -> dict:
        """Parse terrain sliders to extract terrain types and flex rating"""
        terrain_data = {}
        terrain_scores = {}

        try:
            sliders = self.driver.find_elements(By.CSS_SELECTOR, "div.tech-slider")

            for slider in sliders:
                try:
                    # Check for title
                    title_elements = slider.find_elements(
                        By.CSS_SELECTOR, "h5.tech-slider-title"
                    )
                    title = title_elements[0].text.strip() if title_elements else None

                    # If no title, check for terrain name in string-unit
                    if not title:
                        terrain_elements = slider.find_elements(
                            By.CSS_SELECTOR, "div.string-unit"
                        )
                        if terrain_elements:
                            title = terrain_elements[0].text.strip()

                    if title and title != "Personality":
                        # Count dark ticks
                        dark_ticks = len(
                            slider.find_elements(
                                By.CSS_SELECTOR, "span.tech-slider-tick.dark"
                            )
                        )
                        terrain_scores[title] = dark_ticks

                    elif title == "Personality":
                        # Get flex rating from fill style
                        fill_element = slider.find_element(
                            By.CSS_SELECTOR, "div.tech-slider-fill"
                        )
                        style = fill_element.get_attribute("style")
                        flex_rating = self.parse_flex_rating(style)
                        terrain_data["flex_rating"] = flex_rating
                        terrain_data["response"] = self.flex_to_response(flex_rating)

                except NoSuchElementException:
                    continue
        except:
            pass

        # Determine terrain types
        terrain_types = self.determine_terrain_types(terrain_scores)
        terrain_data["terrain_types"] = terrain_types

        return terrain_data

    def parse_flex_rating(self, style_str: str) -> float:
        """Parse flex rating from personality slider style"""
        width_match = re.search(r"width:\s*calc\((\d+)%", style_str)
        margin_match = re.search(r"margin-left:\s*(\d+)%", style_str)

        if width_match and margin_match:
            width = int(width_match.group(1))
            margin_left = int(margin_match.group(1))
            flex_rating = ((width - 10) + margin_left) / 10.0
            return round(flex_rating, 1)

        return None

    def flex_to_response(self, flex_rating: float) -> str:
        """Convert flex rating to response text"""
        if flex_rating is None:
            return None
        if flex_rating <= 3:
            return "Soft"
        elif flex_rating <= 6:
            return "Medium"
        else:
            return "Stiff"

    def determine_terrain_types(self, terrain_scores: dict) -> list:
        """Determine terrain types using threshold logic"""
        if not terrain_scores:
            return None

        for threshold in range(7, 0, -1):
            candidates = {k: v for k, v in terrain_scores.items() if v >= threshold}

            if not candidates:
                continue

            count = len(candidates)

            if count == 1:
                return list(candidates.keys())
            elif count == 2:
                return list(candidates.keys())
            elif count >= 3:
                sorted_terrains = sorted(
                    candidates.items(), key=lambda x: x[1], reverse=True
                )
                top_score = sorted_terrains[0][1]
                second_score = sorted_terrains[1][1]

                if sorted_terrains[2][1] < second_score:
                    return [sorted_terrains[0][0], sorted_terrains[1][0]]
                elif sorted_terrains[1][1] < top_score:
                    return [sorted_terrains[0][0]]
                else:
                    return list(candidates.keys())

        return list(terrain_scores.keys()) if terrain_scores else None

    def parse_size_chart(self) -> list:
        """Parse the size chart table"""
        size_chart_data = []

        try:
            # Find the size chart container
            size_chart = self.driver.find_element(By.CSS_SELECTOR, "div.size-chart")

            # Check if there's an expand button and click it
            try:
                expand_buttons = size_chart.find_elements(
                    By.CSS_SELECTOR, "button.expand-size-chart-button"
                )
                if expand_buttons:
                    self.driver.execute_script(
                        "arguments[0].click();", expand_buttons[0]
                    )
                    time.sleep(0.5)
            except:
                pass

            # Now find the table
            table = size_chart.find_element(By.CSS_SELECTOR, "table.size-chart-table")

            # Extract board sizes from header
            headers = table.find_elements(By.CSS_SELECTOR, "thead tr th")
            board_sizes = [h.text.strip() for h in headers[1:] if h.text.strip()]

            # Extract all rows
            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
            row_data = {}

            for row in rows:
                try:
                    label = row.find_element(By.CSS_SELECTOR, "th").text.strip()
                    values = [
                        td.text.strip()
                        for td in row.find_elements(By.CSS_SELECTOR, "td")
                    ]
                    row_data[label] = values
                except:
                    continue

            # Build size entries
            for idx, size_str in enumerate(board_sizes):
                is_wide = "W" in size_str
                size_cm = float(size_str.replace("W", ""))

                size_entry = {"size_cm": size_cm, "wide": is_wide}

                if "Weight Range" in row_data and idx < len(row_data["Weight Range"]):
                    (
                        size_entry["rider_weight_min_lbs"],
                        size_entry["rider_weight_max_lbs"],
                    ) = self.parse_weight_range(row_data["Weight Range"][idx])

                if "Waist Width" in row_data and idx < len(row_data["Waist Width"]):
                    size_entry["waist_width_mm"] = self.parse_mm(
                        row_data["Waist Width"][idx]
                    )

                if "Running Length" in row_data and idx < len(
                    row_data["Running Length"]
                ):
                    size_entry["running_length_mm"] = self.parse_mm(
                        row_data["Running Length"][idx]
                    )

                if "Sidecut Radius" in row_data and idx < len(
                    row_data["Sidecut Radius"]
                ):
                    size_entry["sidecut_radius_m"] = self.parse_meters(
                        row_data["Sidecut Radius"][idx]
                    )

                if "Sidecut Depth" in row_data and idx < len(row_data["Sidecut Depth"]):
                    size_entry["sidecut_depth_mm"] = self.parse_mm(
                        row_data["Sidecut Depth"][idx]
                    )

                if "Stance Width" in row_data and idx < len(row_data["Stance Width"]):
                    size_entry["reference_stance_in"] = self.parse_mm_to_inches(
                        row_data["Stance Width"][idx]
                    )

                if "Stance Location" in row_data and idx < len(
                    row_data["Stance Location"]
                ):
                    size_entry["setback_in"] = self.parse_setback(
                        row_data["Stance Location"][idx]
                    )

                if "Nose Width" in row_data and idx < len(row_data["Nose Width"]):
                    size_entry["tip_width_mm"] = self.parse_mm(
                        row_data["Nose Width"][idx]
                    )

                if "Tail Width" in row_data and idx < len(row_data["Tail Width"]):
                    size_entry["tail_width_mm"] = self.parse_mm(
                        row_data["Tail Width"][idx]
                    )

                if "Effective Edge" in row_data and idx < len(
                    row_data["Effective Edge"]
                ):
                    size_entry["effective_edge_mm"] = self.parse_mm(
                        row_data["Effective Edge"][idx]
                    )

                if "Binding Sizes" in row_data and idx < len(row_data["Binding Sizes"]):
                    size_entry["recommended_binding_sizes"] = [
                        row_data["Binding Sizes"][idx]
                    ]

                try:
                    size_obj = SizeChart(**size_entry)
                    size_chart_data.append(size_obj)
                except Exception as e:
                    print(f"    ⚠ Error creating size {size_str}: {e}")
        except Exception as e:
            print(f"    ⚠ Could not parse size chart: {e}")

        return size_chart_data if size_chart_data else None

    def parse_weight_range(self, weight_str: str) -> tuple:
        """Parse weight range"""
        match = re.search(r"(\d+)-(\d+)\s*lbs", weight_str)
        if match:
            return (float(match.group(1)), float(match.group(2)))
        match = re.search(r"(\d+)-(\d+)\s*lbs\.\+", weight_str)
        if match:
            return (float(match.group(1)), None)
        return (None, None)

    def parse_mm(self, mm_str: str) -> float:
        """Parse millimeter value"""
        match = re.search(r"([\d.]+)\s*mm", mm_str)
        return float(match.group(1)) if match else None

    def parse_meters(self, m_str: str) -> float:
        """Parse meter value"""
        match = re.search(r"([\d.]+)\s*m", m_str)
        return float(match.group(1)) if match else None

    def parse_mm_to_inches(self, mm_str: str) -> float:
        """Parse mm and convert to inches"""
        mm_value = self.parse_mm(mm_str)
        return round(mm_value / 25.4, 2) if mm_value else None

    def parse_setback(self, setback_str: str) -> float:
        """Parse setback value"""
        try:
            setback_mm = float(setback_str)
            return round(abs(setback_mm) / 25.4, 2)
        except:
            return None

    def run(self):
        """Main scraper execution"""
        self.setup_driver()

        try:
            # Get all product URLs from catalog
            catalog_url = "https://www.burton.com/us/en/c/snowboarding-snowboards"
            products = self.get_product_urls_and_images(catalog_url)

            # In DEBUG mode, only scrape first product
            if self.DEBUG_MODE:
                products = products[:1]
                print(f"\nDEBUG MODE: Only scraping first product")

            # Scrape each product
            print("\n" + "=" * 60)
            print("PHASE 2: Scraping product pages")
            print("=" * 60)

            for idx, product in enumerate(products, 1):
                print(f"\n[{idx}/{len(products)}]")
                board = self.scrape_product(product["url"], product["image_url"])
                if board:
                    self.scraped_boards.append(board)
                time.sleep(2)  # Be respectful

            # Save output
            self.save_output()

        finally:
            if self.driver:
                self.driver.quit()

    def save_output(self):
        """Save scraped data to JSON"""
        print("\n" + "=" * 60)
        print("PHASE 3: Saving output")
        print("=" * 60)

        output = ScraperOutput(
            brand="Burton",
            brand_url="https://www.burton.com",
            scraped_at=datetime.now(),
            scraper_version="1.0.0",
            boards=self.scraped_boards,
            total_boards=len(self.scraped_boards),
        )

        output_dir = Path(__file__).parent.parent / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / "Burton.json"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output.model_dump_json(indent=2))

        print(f"✓ Saved {len(self.scraped_boards)} boards to {output_file}")
        print("=" * 60)


if __name__ == "__main__":
    """
    To run this scraper:

    1. Install dependencies:
       pip install selenium pydantic

    2. Make sure Firefox is installed

    3. Run in DEBUG mode (scrapes 1 board):
       python burton_spider.py

    4. Set DEBUG_MODE = False to scrape all boards
    """
    scraper = BurtonScraper(headless=True)
    scraper.run()
