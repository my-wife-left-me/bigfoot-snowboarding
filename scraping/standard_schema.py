"""
Standard JSON Schema for Snowboard Scraper Output

This schema defines the standardized format that ALL brand-specific scrapers
must output. The universal importer will read this format.

Design principles:
1. Brand-agnostic field names
2. Nullable fields for missing data
3. Consistent data types across brands
4. Support for both metric and imperial measurements
5. Arrays for multi-value fields (ability_levels, terrain_types, etc.)
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, field_validator


class SizeChart(BaseModel):
    """Individual size/length option for a board model"""

    # Required
    size_cm: float = Field(..., description="Board length in centimeters (e.g., 154.0)")
    wide: bool = Field(default=False, description="Whether this is a wide version")

    # Dimensions (all optional, in mm)
    effective_edge_mm: Optional[float] = Field(
        None, description="Effective edge length in mm"
    )
    waist_width_mm: Optional[float] = Field(None, description="Waist width in mm")
    tip_width_mm: Optional[float] = Field(None, description="Tip width in mm")
    tail_width_mm: Optional[float] = Field(None, description="Tail width in mm")
    running_length_mm: Optional[float] = Field(None, description="Running length in mm")

    # Sidecut measurements (in meters)
    sidecut_radius_m: Optional[float] = Field(
        None, description="Primary sidecut radius in meters"
    )
    sidecut_entry_radius_m: Optional[float] = Field(
        None, description="Entry radius (for multi-radius sidecuts)"
    )
    sidecut_focus_radius_m: Optional[float] = Field(
        None, description="Focus/center radius"
    )
    sidecut_exit_radius_m: Optional[float] = Field(None, description="Exit radius")
    sidecut_depth_mm: Optional[float] = Field(None, description="Sidecut depth in mm")

    # Stance measurements (in inches)
    reference_stance_in: Optional[float] = Field(
        None, description="Reference stance width in inches"
    )
    min_stance_in: Optional[float] = Field(None, description="Minimum stance width")
    max_stance_in: Optional[float] = Field(None, description="Maximum stance width")
    setback_in: Optional[float] = Field(None, description="Stance setback in inches")

    # Other specs
    insert_count: Optional[int] = Field(None, description="Number of insert holes")

    # Rider recommendations
    rider_weight_min_lbs: Optional[float] = Field(
        None, description="Minimum rider weight in lbs"
    )
    rider_weight_max_lbs: Optional[float] = Field(
        None, description="Maximum rider weight in lbs"
    )

    # Boot/binding compatibility
    recommended_boot_sizes: Optional[List[str]] = Field(
        None, description="Recommended boot sizes (e.g., ['8-10', '10.5-12'])"
    )
    recommended_binding_sizes: Optional[List[str]] = Field(
        None, description="Recommended binding sizes (e.g., ['M', 'L'])"
    )


class Board(BaseModel):
    """Individual snowboard model"""

    # Required fields
    name: str = Field(
        ..., description="Full product name including brand (e.g., 'Burton Custom X')"
    )
    model_year: Optional[int] = Field(None, description="Model year (e.g., 2025)")

    # URLs
    url: HttpUrl = Field(..., description="Product page URL")
    image_url: Optional[HttpUrl] = Field(None, description="Primary product image URL")

    # Pricing
    price: Optional[float] = Field(None, description="MSRP in USD")

    # Classification
    gender: Optional[str] = Field(
        None, description="Target gender: 'MENS', 'WOMENS', 'UNISEX', or 'KIDS'"
    )

    # Profile (camber/rocker)
    profile_type: Optional[str] = Field(
        None, description="Profile type (e.g., 'Camber', 'Flying V', 'Flat Top')"
    )
    profile_description: Optional[str] = Field(
        None, description="Detailed profile description"
    )

    # Shape
    shape_type: Optional[str] = Field(
        None, description="Shape type (e.g., 'Directional', 'Twin', 'Directional Twin')"
    )
    shape_description: Optional[str] = Field(
        None, description="Detailed shape description"
    )

    # Flex and Response
    flex_rating: Optional[float] = Field(
        None, ge=1.0, le=10.0, description="Flex rating on 1-10 scale"
    )
    response: Optional[str] = Field(
        None, description="Response type (e.g., 'Stiff', 'Medium', 'Soft', 'Playful')"
    )

    # Multi-value classifications
    ability_levels: Optional[List[str]] = Field(
        None, description="Target ability levels (e.g., ['Beginner', 'Intermediate'])"
    )
    terrain_types: Optional[List[str]] = Field(
        None,
        description="Terrain specialties (e.g., ['All-Mountain', 'Park', 'Powder'])",
    )
    technologies: Optional[List[str]] = Field(
        None,
        description="Brand technologies/features (e.g., ['Flying V', 'Squeezebox'])",
    )

    # Descriptions
    description: Optional[str] = Field(
        None, description="Marketing description or tagline"
    )
    full_description: Optional[str] = Field(
        None, description="Full product description"
    )

    # Size options
    size_chart: Optional[List[SizeChart]] = Field(
        None, description="Available sizes with detailed specs"
    )

    # Additional metadata (for debugging/reference)
    raw_data: Optional[Dict[str, Any]] = Field(
        None, description="Original scraped data for reference"
    )

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v):
        if v is not None:
            allowed = ["MENS", "WOMENS", "UNISEX", "KIDS"]
            if v.upper() not in allowed:
                raise ValueError(f"Gender must be one of {allowed}")
        return v.upper() if v else None


class ScraperOutput(BaseModel):
    """Top-level output from a brand scraper"""

    # Metadata
    brand: str = Field(..., description="Brand name (e.g., 'Burton', 'RIDE')")
    brand_url: HttpUrl = Field(..., description="Brand website URL")
    scraped_at: datetime = Field(
        default_factory=datetime.now, description="Timestamp of scrape"
    )
    scraper_version: str = Field(default="1.0.0", description="Version of the scraper")

    # Data
    boards: List[Board] = Field(..., description="List of scraped boards")

    # Statistics
    total_boards: int = Field(..., description="Total number of boards scraped")

    @field_validator("total_boards")
    @classmethod
    def validate_total(cls, v, info):
        if "boards" in info.data:
            return len(info.data["boards"])
        return v


# Example usage and validation
def create_example():
    """Create an example output to demonstrate the schema"""
    example = ScraperOutput(
        brand="Burton",
        brand_url="https://www.burton.com",
        scraped_at=datetime.now(),
        scraper_version="1.0.0",
        total_boards=1,
        boards=[
            Board(
                name="Burton Custom Camber",
                model_year=2025,
                url="https://www.burton.com/us/en/p/mens-burton-custom-camber-snowboard/W26-106881.html",
                image_url="https://www.burton.com/static/product/W26/1068819AI2RG_1.png",
                price=679.95,
                gender="mens",
                profile_type="Camber",
                profile_description="Pure Camber for precision and pop",
                shape_type="Twin",
                shape_description="Perfectly symmetrical for balanced riding",
                flex_rating=6.0,
                response="Medium",
                ability_levels=["Intermediate", "Advanced", "Expert"],
                terrain_types=["All-Mountain", "Park"],
                technologies=["Squeezebox", "Pro-Tip"],
                description="A legendary poppy, versatile, and fun board",
                size_chart=[
                    SizeChart(
                        size_cm=154.0,
                        wide=False,
                        effective_edge_mm=1180.0,
                        waist_width_mm=252.0,
                        tip_width_mm=295.0,
                        tail_width_mm=295.0,
                        sidecut_radius_m=7.8,
                        reference_stance_in=21.5,
                        setback_in=0.0,
                        rider_weight_min_lbs=120.0,
                        rider_weight_max_lbs=180.0,
                    )
                ],
            )
        ],
    )
    return example


def validate_json_file(filepath: str) -> ScraperOutput:
    """
    Validate a JSON file against the schema

    Args:
        filepath: Path to JSON file

    Returns:
        Validated ScraperOutput object

    Raises:
        ValidationError if JSON doesn't match schema
    """
    import json

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return ScraperOutput(**data)


if __name__ == "__main__":
    # Create and print example
    example = create_example()
    print(example.model_dump_json(indent=2))

    # Validate the example
    print("\n✓ Schema validation passed!")
