"""
Universal Supabase Importer for Snowboard Data

This importer reads standardized JSON files (following standard_schema.py)
and imports them into Supabase. It handles:
- Alias mapping and creation
- Brand management
- Board model and size insertion
- Junction table relationships
- Dry run mode for validation

Usage:
    python -m scraping.supabase_importer --file output/Burton.json --mode analyze
    python -m scraping.supabase_importer --file output/Burton.json --mode dry-run
    python -m scraping.supabase_importer --file output/Burton.json --mode live
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import sys
import re

# Load environment variables from project root
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Please set SUPABASE_URL and SUPABASE_KEY in your .env file")


class UniversalImporter:
    """Universal importer for standardized snowboard JSON data"""

    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.brand_id: Optional[int] = None
        self.alias_cache = {
            "shape": {},
            "profile": {},
            "response_type": {},
            "ability_level": {},
            "terrain_type": {},
        }

    def load_json(self, filepath: str) -> Dict[str, Any]:
        """Load and return JSON data"""
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def analyze_data(self, data: Dict[str, Any]) -> Dict[str, set]:
        """
        Analyze the JSON data and extract all unique values that need aliases.
        Returns a dictionary of sets for each alias type.
        """
        print("\n" + "=" * 80)
        print("DATA ANALYSIS - Unique Values Found")
        print("=" * 80)

        unique_values = {
            "shapes": set(),
            "profiles": set(),
            "response_types": set(),
            "ability_levels": set(),
            "terrain_types": set(),
        }

        # Standard values that should already exist
        STANDARD_ABILITY_LEVELS = {"Beginner", "Intermediate", "Advanced", "Expert"}
        STANDARD_TERRAIN_TYPES = {"Freestyle", "Freeride", "All-Mountain"}

        boards = data.get("boards", [])

        for board in boards:
            # Shapes
            if board.get("shape_type"):
                unique_values["shapes"].add(board["shape_type"])

            # Profiles
            if board.get("profile_type"):
                unique_values["profiles"].add(board["profile_type"])

            # Response types
            if board.get("response"):
                unique_values["response_types"].add(board["response"])

            # Ability levels
            if board.get("ability_levels"):
                for level in board["ability_levels"]:
                    unique_values["ability_levels"].add(level)

            # Terrain types
            if board.get("terrain_types"):
                for terrain in board["terrain_types"]:
                    unique_values["terrain_types"].add(terrain)

        # Print summary
        print(f"\n📊 Brand: {data.get('brand', 'Unknown')}")
        print(f"📊 Total boards: {len(boards)}")
        print(f"📊 Scraped at: {data.get('scraped_at', 'Unknown')}")

        # Check for non-standard ability levels or terrain types
        non_standard_abilities = (
            unique_values["ability_levels"] - STANDARD_ABILITY_LEVELS
        )
        non_standard_terrains = unique_values["terrain_types"] - STANDARD_TERRAIN_TYPES

        if non_standard_abilities:
            print(f"\n⚠️  WARNING: Non-standard ability levels found:")
            for val in sorted(non_standard_abilities):
                print(
                    f"   • {val} (expected: {', '.join(sorted(STANDARD_ABILITY_LEVELS))})"
                )

        if non_standard_terrains:
            print(f"\n⚠️  WARNING: Non-standard terrain types found:")
            for val in sorted(non_standard_terrains):
                print(
                    f"   • {val} (expected: {', '.join(sorted(STANDARD_TERRAIN_TYPES))})"
                )

        print(f"\n📦 Shape Types ({len(unique_values['shapes'])}) - Need aliases:")
        for val in sorted(unique_values["shapes"]):
            print(f"   • {val}")

        print(f"\n📦 Profile Types ({len(unique_values['profiles'])}) - Need aliases:")
        for val in sorted(unique_values["profiles"]):
            print(f"   • {val}")

        print(
            f"\n📦 Response Types ({len(unique_values['response_types'])}) - Need aliases:"
        )
        for val in sorted(unique_values["response_types"]):
            print(f"   • {val}")

        if unique_values["terrain_types"]:
            print(
                f"\n📦 Terrain Types ({len(unique_values['terrain_types'])}) - Need aliases:"
            )
            for val in sorted(unique_values["terrain_types"]):
                print(f"   • {val}")

        return unique_values

    def generate_sql_inserts(self, unique_values: Dict[str, set], brand_name: str):
        """Generate SQL statements for brand and aliases (manual mapping required)"""
        print("\n" + "=" * 80)
        print("SQL GENERATION - Manual Setup Required")
        print("=" * 80)

        print("\n-- STEP 1: Create brand (if not exists)")
        print(f"INSERT INTO brand (name, website_url)")
        print(f"VALUES ('{brand_name}', '<brand_website_url>')")
        print(f"ON CONFLICT (name) DO NOTHING;")

        print("\n-- STEP 2: Get the brand ID")
        print(f"SELECT id FROM brand WHERE name = '{brand_name}';")
        print("-- Copy this ID and use it below as <brand_id>")

        print("\n" + "=" * 80)
        print("ALIASES NEEDED - Manual Mapping Required")
        print("=" * 80)
        print("\nYou need to map these brand-specific terms to standard values.")
        print("Review each list and decide which standard value it corresponds to.")

        # Shapes
        print(f"\n-- SHAPES: Map these {brand_name} terms to standard shapes")
        print(
            "-- Example standard shapes: directional, twin, directional_twin, tapered_directional"
        )
        print("-- Format: INSERT INTO shape_alias (shape_id, brand_id, alias_name)")
        print("--         SELECT id, <brand_id>, '<brand_alias>'")
        print("--         FROM shape WHERE standard_name = '<standard_name>';")
        print()
        for shape in sorted(unique_values["shapes"]):
            print(f"-- '{shape}' -> which standard shape?")

        # Profiles
        print(f"\n-- PROFILES: Map these {brand_name} terms to standard profiles")
        print(
            "-- Example standard profiles: camber, rocker, flat, hybrid_camber, hybrid_rocker"
        )
        print("-- Format: INSERT INTO profile_alias (profile_id, brand_id, alias_name)")
        print("--         SELECT id, <brand_id>, '<brand_alias>'")
        print("--         FROM profile WHERE standard_name = '<standard_name>';")
        print()
        for profile in sorted(unique_values["profiles"]):
            print(f"-- '{profile}' -> which standard profile?")

        # Response types
        print(
            f"\n-- RESPONSE TYPES: Map these {brand_name} terms to standard response types"
        )
        print("-- Example standard responses: soft, medium, stiff, playful, responsive")
        print(
            "-- Format: INSERT INTO response_type_alias (response_type_id, brand_id, alias_name)"
        )
        print("--         SELECT id, <brand_id>, '<brand_alias>'")
        print("--         FROM response_type WHERE standard_name = '<standard_name>';")
        print()
        for response in sorted(unique_values["response_types"]):
            print(f"-- '{response}' -> which standard response?")

        # Terrain types
        if unique_values["terrain_types"]:
            print(
                f"\n-- TERRAIN TYPES: Map these {brand_name} terms to standard terrain types"
            )
            print(
                "-- Example standard terrain types: Freestyle, Freeride, All-Mountain"
            )
            print(
                "-- Format: INSERT INTO terrain_type_alias (terrain_type_id, brand_id, alias_name)"
            )
            print("--         SELECT id, <brand_id>, '<brand_alias>'")
            print("--         FROM terrain_type WHERE name = '<standard_name>';")
            print()
            for terrain in sorted(unique_values["terrain_types"]):
                print(f"-- '{terrain}' -> which standard terrain type?")

        print("\n" + "=" * 80)
        print("EXAMPLE: How to create aliases after mapping")
        print("=" * 80)
        print("\n-- Example for Burton 'Camber' -> standard 'camber':")
        print(f"INSERT INTO profile_alias (profile_id, brand_id, alias_name)")
        print(f"SELECT p.id, <brand_id>, 'Camber'")
        print(f"FROM profile p WHERE p.standard_name = 'camber'")
        print(f"ON CONFLICT (brand_id, alias_name) DO NOTHING;")

        print("\n-- Example for Burton 'Twin' -> standard 'twin':")
        print(f"INSERT INTO shape_alias (shape_id, brand_id, alias_name)")
        print(f"SELECT s.id, <brand_id>, 'Twin'")
        print(f"FROM shape s WHERE s.standard_name = 'twin'")
        print(f"ON CONFLICT (brand_id, alias_name) DO NOTHING;")

        print("\n-- Example for Burton 'All-Mountain' -> standard 'All-Mountain':")
        print(f"INSERT INTO terrain_type_alias (terrain_type_id, brand_id, alias_name)")
        print(f"SELECT t.id, <brand_id>, 'All-Mountain'")
        print(f"FROM terrain_type t WHERE t.name = 'All-Mountain'")
        print(f"ON CONFLICT (brand_id, alias_name) DO NOTHING;")

        print("\n" + "=" * 80)
        print("HELPFUL QUERIES: View existing standard values")
        print("=" * 80)
        print("\n-- View all standard shapes:")
        print(
            "SELECT id, standard_name, description FROM shape ORDER BY standard_name;"
        )
        print("\n-- View all standard profiles:")
        print(
            "SELECT id, standard_name, description FROM profile ORDER BY standard_name;"
        )
        print("\n-- View all standard response types:")
        print(
            "SELECT id, standard_name, description FROM response_type ORDER BY standard_name;"
        )
        print("\n-- View all ability levels:")
        print("SELECT id, name FROM ability_level ORDER BY sort_order;")
        print("\n-- View all terrain types:")
        print("SELECT id, name FROM terrain_type ORDER BY name;")

        print("\n" + "=" * 80)

    def standardize_name(self, name: str) -> str:
        """Convert a name to standard_name format (lowercase, underscores)"""
        return name.lower().replace(" ", "_").replace("-", "_")

    def load_alias_cache(self, brand_id: int):
        """Load all aliases and IDs from database into cache"""
        print("\n📂 Loading aliases from database...")

        # Load shape aliases for this brand
        shapes = (
            self.supabase.table("shape_alias")
            .select("alias_name, shape_id")
            .eq("brand_id", brand_id)
            .execute()
        )
        for shape in shapes.data:
            self.alias_cache["shape"][shape["alias_name"]] = shape["shape_id"]

        # Load profile aliases for this brand
        profiles = (
            self.supabase.table("profile_alias")
            .select("alias_name, profile_id")
            .eq("brand_id", brand_id)
            .execute()
        )
        for profile in profiles.data:
            self.alias_cache["profile"][profile["alias_name"]] = profile["profile_id"]

        # Load response type aliases for this brand
        responses = (
            self.supabase.table("response_type_alias")
            .select("alias_name, response_type_id")
            .eq("brand_id", brand_id)
            .execute()
        )
        for response in responses.data:
            self.alias_cache["response_type"][response["alias_name"]] = response[
                "response_type_id"
            ]

        # Load ability levels (direct match, no brand association)
        abilities = self.supabase.table("ability_level").select("id, name").execute()
        for ability in abilities.data:
            self.alias_cache["ability_level"][ability["name"]] = ability["id"]

        # Load terrain type aliases for this brand
        terrains = (
            self.supabase.table("terrain_type_alias")
            .select("alias_name, terrain_type_id")
            .eq("brand_id", brand_id)
            .execute()
        )
        for terrain in terrains.data:
            self.alias_cache["terrain_type"][terrain["alias_name"]] = terrain[
                "terrain_type_id"
            ]

        print(f"   ✓ Loaded {len(self.alias_cache['shape'])} shape aliases")
        print(f"   ✓ Loaded {len(self.alias_cache['profile'])} profile aliases")
        print(
            f"   ✓ Loaded {len(self.alias_cache['response_type'])} response type aliases"
        )
        print(f"   ✓ Loaded {len(self.alias_cache['ability_level'])} ability levels")
        print(
            f"   ✓ Loaded {len(self.alias_cache['terrain_type'])} terrain type aliases"
        )

    def get_or_create_brand(
        self, brand_name: str, brand_url: str, scraper_version: str
    ) -> int:
        """Get brand ID or create if doesn't exist"""
        result = (
            self.supabase.table("brand").select("id").eq("name", brand_name).execute()
        )

        if result.data:
            brand_id = result.data[0]["id"]
            # Update last_scraped_at and scraper_version
            self.supabase.table("brand").update(
                {
                    "last_scraped_at": datetime.now(timezone.utc).isoformat(),
                    "scraper_version": scraper_version,
                }
            ).eq("id", brand_id).execute()
            print(f"   ✓ Found existing brand: {brand_name} (ID: {brand_id})")
            return brand_id

        # Create new brand
        brand_data = {
            "name": brand_name,
            "website_url": brand_url,
            "scraper_version": scraper_version,
            "last_scraped_at": datetime.now(timezone.utc).isoformat(),
        }
        result = self.supabase.table("brand").insert(brand_data).execute()
        brand_id = result.data[0]["id"]
        print(f"   ✓ Created new brand: {brand_name} (ID: {brand_id})")
        return brand_id

    def import_boards(self, data: Dict[str, Any], dry_run: bool = True):
        """Import all boards from the JSON data"""

        mode = "🔍 DRY RUN" if dry_run else "⚠️  LIVE IMPORT"
        print("\n" + "=" * 80)
        print(f"{mode} - Starting import process")
        print("=" * 80)

        # Get or create brand
        brand_name = data.get("brand")
        brand_url = data.get("brand_url")
        scraper_version = data.get("scraper_version", "1.0.0")

        if not dry_run:
            self.brand_id = self.get_or_create_brand(
                brand_name, brand_url, scraper_version
            )
            self.load_alias_cache(self.brand_id)
        else:
            print(f"\n   Would process brand: {brand_name}")
            print(f"   Brand URL: {brand_url}")
            print(f"   Scraper version: {scraper_version}")

        boards = data.get("boards", [])
        success_count = 0
        error_count = 0
        missing_aliases = []

        for idx, board_data in enumerate(boards, 1):
            try:
                board_name = board_data.get("name", "Unknown")
                print(f"\n[{idx}/{len(boards)}] Processing: {board_name}")

                # Check for missing aliases
                if not dry_run:
                    missing = self.check_missing_aliases(board_data)
                    if missing:
                        print(f"   ⚠️  Missing aliases: {', '.join(missing)}")
                        missing_aliases.extend(missing)
                        error_count += 1
                        continue

                # Import board
                if dry_run:
                    print(f"   ✓ Would import: {board_name}")
                    print(f"      - Model year: {board_data.get('model_year')}")
                    print(f"      - Gender: {board_data.get('gender')}")
                    print(f"      - Profile: {board_data.get('profile_type')}")
                    print(f"      - Shape: {board_data.get('shape_type')}")
                    print(f"      - Sizes: {len(board_data.get('size_chart', []))}")
                else:
                    board_model_id = self.import_board(board_data)
                    print(f"   ✓ Imported successfully (ID: {board_model_id})")

                success_count += 1

            except Exception as e:
                print(f"   ✗ Error: {str(e)}")
                error_count += 1

        # Summary
        print("\n" + "=" * 80)
        print("IMPORT SUMMARY")
        print("=" * 80)
        print(f"   Success: {success_count}")
        print(f"   Errors: {error_count}")

        if missing_aliases:
            print(f"\n   ⚠️  Missing aliases detected:")
            for alias in set(missing_aliases):
                print(f"      • {alias}")
            print(f"\n   Run the SQL generation step to create these aliases.")

        print("=" * 80 + "\n")

    def check_missing_aliases(self, board_data: Dict[str, Any]) -> List[str]:
        """Check for any missing aliases and return list of missing items"""
        missing = []

        # Check shape
        shape_type = board_data.get("shape_type")
        if shape_type and shape_type not in self.alias_cache["shape"]:
            missing.append(f"shape:{shape_type}")

        # Check profile
        profile_type = board_data.get("profile_type")
        if profile_type and profile_type not in self.alias_cache["profile"]:
            missing.append(f"profile:{profile_type}")

        # Check response type
        response = board_data.get("response")
        if response and response not in self.alias_cache["response_type"]:
            missing.append(f"response:{response}")

        # Check ability levels
        if board_data.get("ability_levels"):
            for level in board_data.get("ability_levels", []):
                if level not in self.alias_cache["ability_level"]:
                    missing.append(f"ability:{level}")

        # Check terrain types
        for terrain in board_data.get("terrain_types", []):
            if terrain not in self.alias_cache["terrain_type"]:
                missing.append(f"terrain:{terrain}")

        return missing

    def import_board(self, board_data: Dict[str, Any]) -> int:
        """Import a single board and return its ID"""

        # Resolve IDs from aliases
        shape_id = self.alias_cache["shape"].get(board_data.get("shape_type"))
        profile_id = self.alias_cache["profile"].get(board_data.get("profile_type"))
        response_type_id = self.alias_cache["response_type"].get(
            board_data.get("response")
        )

        # Prepare board_model data
        board_model_data = {
            "brand_id": self.brand_id,
            "model_name": board_data.get("name"),
            "model_year": board_data.get("model_year"),
            "gender": board_data.get("gender"),
            "profile_id": profile_id,
            "response_type_id": response_type_id,
            "flex_rating": board_data.get("flex_rating"),
            "msrp": board_data.get("price"),
            "source_url": board_data.get("url"),
            "image_url": board_data.get("image_url"),
            "shape_id": shape_id,
        }

        # Check if board already exists
        existing = (
            self.supabase.table("board_model")
            .select("id")
            .eq("brand_id", self.brand_id)
            .eq("model_name", board_data.get("name"))
            .eq("model_year", board_data.get("model_year"))
            .execute()
        )

        if existing.data:
            # Update existing board
            board_model_id = existing.data[0]["id"]
            board_model_data["id"] = board_model_id
            self.supabase.table("board_model").upsert(board_model_data).execute()
        else:
            # Insert new board
            result = (
                self.supabase.table("board_model").insert(board_model_data).execute()
            )
            board_model_id = result.data[0]["id"]

            # Insert ability levels
            if board_data.get("ability_levels"):
                for level in board_data.get("ability_levels", []):
                    level_id = self.alias_cache["ability_level"].get(level)
                    if level_id:
                        self.supabase.table("board_model_ability_level").insert(
                            {
                                "board_model_id": board_model_id,
                                "ability_level_id": level_id,
                            }
                        ).execute()

        # Insert/update terrain types (for both new and existing boards)
        # First, delete existing terrain type relationships to avoid duplicates
        self.supabase.table("board_model_terrain_type").delete().eq(
            "board_model_id", board_model_id
        ).execute()

        # Then insert current terrain types
        for terrain in board_data.get("terrain_types", []):
            terrain_id = self.alias_cache["terrain_type"].get(terrain)
            if terrain_id:
                self.supabase.table("board_model_terrain_type").insert(
                    {
                        "board_model_id": board_model_id,
                        "terrain_type_id": terrain_id,
                    }
                ).execute()

        # Insert/update sizes
        for size_data in board_data.get("size_chart", []):
            self.import_board_size(board_model_id, size_data)

        return board_model_id

    def import_board_size(self, board_model_id: int, size_data: Dict[str, Any]):
        """Import a single board size"""

        size_record = {
            "board_model_id": board_model_id,
            "size_cm": size_data.get("size_cm"),
            "wide": size_data.get("wide", False),
            "effective_edge_mm": size_data.get("effective_edge_mm"),
            "waist_width_mm": size_data.get("waist_width_mm"),
            "tip_width_mm": size_data.get("tip_width_mm"),
            "tail_width_mm": size_data.get("tail_width_mm"),
            "running_length_mm": size_data.get("running_length_mm"),
            "sidecut_radius_m": size_data.get("sidecut_radius_m"),
            "sidecut_entry_radius_m": size_data.get("sidecut_entry_radius_m"),
            "sidecut_focus_radius_m": size_data.get("sidecut_focus_radius_m"),
            "sidecut_exit_radius_m": size_data.get("sidecut_exit_radius_m"),
            "sidecut_depth_mm": size_data.get("sidecut_depth_mm"),
            "reference_stance_in": size_data.get("reference_stance_in"),
            "min_stance_in": size_data.get("min_stance_in"),
            "max_stance_in": size_data.get("max_stance_in"),
            "setback_in": size_data.get("setback_in"),
            "insert_count": size_data.get("insert_count"),
            "rider_weight_min_lbs": size_data.get("rider_weight_min_lbs"),
            "rider_weight_max_lbs": size_data.get("rider_weight_max_lbs"),
        }

        # Check if size already exists
        existing_size = (
            self.supabase.table("board_size")
            .select("id")
            .eq("board_model_id", board_model_id)
            .eq("size_cm", size_data.get("size_cm"))
            .eq("wide", size_data.get("wide", False))
            .execute()
        )

        if existing_size.data:
            size_record["id"] = existing_size.data[0]["id"]

        self.supabase.table("board_size").upsert(size_record).execute()


def main():
    parser = argparse.ArgumentParser(
        description="Universal Snowboard Data Importer for Supabase"
    )
    parser.add_argument(
        "--file",
        type=str,
        required=True,
        help="Path to JSON file (e.g., output/Burton.json)",
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["analyze", "dry-run", "live"],
        default="dry-run",
        help="Import mode: analyze (just show data), dry-run (validate), or live (actually import)",
    )

    args = parser.parse_args()

    # Load JSON file
    filepath = Path(args.file)
    if not filepath.exists():
        print(f"❌ Error: File not found: {filepath}")
        return

    importer = UniversalImporter(SUPABASE_URL, SUPABASE_KEY)
    data = importer.load_json(filepath)

    if args.mode == "analyze":
        # Just analyze and generate SQL
        unique_values = importer.analyze_data(data)
        importer.generate_sql_inserts(unique_values, data.get("brand"))

    elif args.mode == "dry-run":
        # Analyze + dry run
        unique_values = importer.analyze_data(data)
        print("\n💡 Tip: Run with --mode=analyze to see SQL for missing aliases")
        importer.import_boards(data, dry_run=True)

    elif args.mode == "live":
        # Actually import
        importer.import_boards(data, dry_run=False)


if __name__ == "__main__":
    """
    Usage examples:

    1. Analyze data and generate SQL:
       python -m scraping.supabase_importer --file scraping/output/Burton.json --mode analyze

    2. Dry run (validate without importing):
       python -m scraping.supabase_importer --file scraping/output/Burton.json --mode dry-run

    3. Live import:
       python -m scraping.supabase_importer --file scraping/output/Burton.json --mode live
    """
    main()
