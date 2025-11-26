-- Tables with no dependencies first
create table public.ability_level (
  id serial not null,
  name character varying(50) not null,
  sort_order integer null,
  created_at timestamp with time zone null default now(),
  constraint ability_level_pkey primary key (id),
  constraint ability_level_name_key unique (name)
) TABLESPACE pg_default;

create table public.binding_size (
  id serial not null,
  size character varying(10) not null,
  gender character varying(20) null,
  created_at timestamp with time zone null default now(),
  constraint binding_size_pkey primary key (id),
  constraint binding_size_size_key unique (size)
) TABLESPACE pg_default;

create table public.boot_size (
  id serial not null,
  us_size character varying(10) not null,
  eu_size character varying(10) null,
  uk_size character varying(10) null,
  mondo_cm numeric(4, 1) null,
  gender character varying(20) null,
  created_at timestamp with time zone null default now(),
  constraint boot_size_pkey primary key (id),
  constraint boot_size_us_size_gender_key unique (us_size, gender)
) TABLESPACE pg_default;

create table public.brand (
  id serial not null,
  name character varying(100) not null,
  website_url character varying(500) null,
  scraper_version character varying(50) null,
  last_scraped_at timestamp with time zone null,
  created_at timestamp with time zone null default now(),
  updated_at timestamp with time zone null default now(),
  constraint brand_pkey primary key (id),
  constraint brand_name_key unique (name)
) TABLESPACE pg_default;

create trigger update_brand_updated_at BEFORE
update on brand for EACH row
execute FUNCTION update_updated_at_column ();

create table public.profile (
  id serial not null,
  standard_name character varying(50) not null,
  created_at timestamp with time zone null default now(),
  constraint profile_pkey primary key (id),
  constraint profile_standard_name_key unique (standard_name)
) TABLESPACE pg_default;

create table public.response_type (
  id serial not null,
  standard_name character varying(50) not null,
  created_at timestamp with time zone null default now(),
  constraint response_type_pkey primary key (id),
  constraint response_type_standard_name_key unique (standard_name)
) TABLESPACE pg_default;

create table public.shape (
  id serial not null,
  standard_name character varying(50) not null,
  created_at timestamp with time zone null default now(),
  constraint shape_pkey primary key (id),
  constraint shape_standard_name_key unique (standard_name)
) TABLESPACE pg_default;

create table public.terrain_type (
  id serial not null,
  name character varying(50) not null,
  created_at timestamp with time zone null default now(),
  constraint terrain_type_pkey primary key (id),
  constraint terrain_type_name_key unique (name)
) TABLESPACE pg_default;

-- Tables with single-level dependencies
create table public.profile_alias (
  id serial not null,
  profile_id integer null,
  brand_id integer null,
  alias_name character varying(100) not null,
  created_at timestamp with time zone null default now(),
  constraint profile_alias_pkey primary key (id),
  constraint profile_alias_brand_id_alias_name_key unique (brand_id, alias_name),
  constraint profile_alias_brand_id_fkey foreign KEY (brand_id) references brand (id) on delete CASCADE,
  constraint profile_alias_profile_id_fkey foreign KEY (profile_id) references profile (id) on delete CASCADE
) TABLESPACE pg_default;

create index IF not exists idx_profile_alias_brand on public.profile_alias using btree (brand_id) TABLESPACE pg_default;

create table public.response_type_alias (
  id serial not null,
  response_type_id integer null,
  brand_id integer null,
  alias_name character varying(100) not null,
  created_at timestamp with time zone null default now(),
  constraint response_type_alias_pkey primary key (id),
  constraint response_type_alias_brand_id_alias_name_key unique (brand_id, alias_name),
  constraint response_type_alias_brand_id_fkey foreign KEY (brand_id) references brand (id) on delete CASCADE,
  constraint response_type_alias_response_type_id_fkey foreign KEY (response_type_id) references response_type (id) on delete CASCADE
) TABLESPACE pg_default;

create table public.shape_alias (
  id serial not null,
  shape_id integer null,
  brand_id integer null,
  alias_name character varying(100) not null,
  created_at timestamp with time zone null default now(),
  constraint shape_alias_pkey primary key (id),
  constraint shape_alias_brand_id_alias_name_key unique (brand_id, alias_name),
  constraint shape_alias_brand_id_fkey foreign KEY (brand_id) references brand (id) on delete CASCADE,
  constraint shape_alias_shape_id_fkey foreign KEY (shape_id) references shape (id) on delete CASCADE
) TABLESPACE pg_default;

create index IF not exists idx_shape_alias_brand on public.shape_alias using btree (brand_id) TABLESPACE pg_default;

create table public.board_model (
  id serial not null,
  brand_id integer null,
  model_name character varying(200) not null,
  model_year integer null,
  profile_id integer null,
  flex_rating numeric(3, 1) null,
  source_url character varying(1000) null,
  image_url character varying(1000) null,
  created_at timestamp with time zone null default now(),
  updated_at timestamp with time zone null default now(),
  msrp numeric(10, 2) null,
  response_type_id integer null,
  gender character varying null,
  shape_id integer null,
  constraint board_model_pkey primary key (id),
  constraint board_model_brand_id_model_name_model_year_key unique (brand_id, model_name, model_year),
  constraint board_model_brand_id_fkey foreign KEY (brand_id) references brand (id) on delete CASCADE,
  constraint board_model_profile_id_fkey foreign KEY (profile_id) references profile (id),
  constraint board_model_response_type_id_fkey foreign KEY (response_type_id) references response_type (id),
  constraint board_model_flex_rating_check check (
    (
      (flex_rating >= (1)::numeric)
      and (flex_rating <= (10)::numeric)
    )
  )
) TABLESPACE pg_default;

create index IF not exists idx_board_model_brand on public.board_model using btree (brand_id) TABLESPACE pg_default;

create index IF not exists idx_board_model_profile on public.board_model using btree (profile_id) TABLESPACE pg_default;

create index IF not exists idx_board_model_year on public.board_model using btree (model_year) TABLESPACE pg_default;

create index IF not exists idx_board_model_flex on public.board_model using btree (flex_rating) TABLESPACE pg_default;

create trigger update_board_model_updated_at BEFORE
update on board_model for EACH row
execute FUNCTION update_updated_at_column ();

-- Junction tables for board_model
create table public.board_model_ability_level (
  board_model_id integer not null,
  ability_level_id integer not null,
  constraint board_model_ability_level_pkey primary key (board_model_id, ability_level_id),
  constraint board_model_ability_level_ability_level_id_fkey foreign KEY (ability_level_id) references ability_level (id) on delete CASCADE,
  constraint board_model_ability_level_board_model_id_fkey foreign KEY (board_model_id) references board_model (id) on delete CASCADE
) TABLESPACE pg_default;

create table public.board_model_terrain_type (
  board_model_id integer not null,
  terrain_type_id integer not null,
  constraint board_model_terrain_type_pkey primary key (board_model_id, terrain_type_id),
  constraint board_model_terrain_type_board_model_id_fkey foreign KEY (board_model_id) references board_model (id) on delete CASCADE,
  constraint board_model_terrain_type_terrain_type_id_fkey foreign KEY (terrain_type_id) references terrain_type (id) on delete CASCADE
) TABLESPACE pg_default;

create table public.terrain_type_alias (
  id serial not null,
  terrain_type_id integer not null,
  brand_id integer not null,
  alias_name character varying(100) not null,
  created_at timestamp with time zone null default now(),
  constraint terrain_type_alias_pkey primary key (id),
  constraint terrain_type_alias_brand_id_alias_name_key unique (brand_id, alias_name),
  constraint terrain_type_alias_brand_id_fkey foreign KEY (brand_id) references brand (id) on delete CASCADE,
  constraint terrain_type_alias_terrain_type_id_fkey foreign KEY (terrain_type_id) references terrain_type (id) on delete CASCADE
) TABLESPACE pg_default;

create index IF not exists idx_terrain_type_alias_brand on public.terrain_type_alias using btree (brand_id) TABLESPACE pg_default;

create table public.board_size (
  id serial not null,
  board_model_id integer null,
  size_cm numeric(5, 1) not null,
  effective_edge_mm numeric(6, 1) null,
  waist_width_mm numeric(5, 1) null,
  tip_width_mm numeric(5, 1) null,
  tail_width_mm numeric(5, 1) null,
  running_length_mm numeric(6, 1) null,
  sidecut_radius_m numeric(5, 2) null,
  sidecut_entry_radius_m numeric(5, 2) null,
  sidecut_focus_radius_m numeric(5, 2) null,
  sidecut_exit_radius_m numeric(5, 2) null,
  sidecut_depth_mm numeric(5, 1) null,
  reference_stance_in numeric(4, 2) null,
  min_stance_in numeric(4, 2) null,
  max_stance_in numeric(4, 2) null,
  setback_in numeric(4, 2) null,
  insert_count integer null,
  rider_weight_min_lbs numeric(5, 1) null,
  rider_weight_max_lbs numeric(5, 1) null,
  created_at timestamp with time zone null default now(),
  updated_at timestamp with time zone null default now(),
  wide boolean null default false,
  constraint board_size_pkey primary key (id),
  constraint board_size_board_model_id_size_cm_wide_key unique (board_model_id, size_cm, wide),
  constraint board_size_board_model_id_fkey foreign KEY (board_model_id) references board_model (id) on delete CASCADE
) TABLESPACE pg_default;

create index IF not exists idx_board_size_model on public.board_size using btree (board_model_id) TABLESPACE pg_default;

create index IF not exists idx_board_size_size on public.board_size using btree (size_cm) TABLESPACE pg_default;

create index IF not exists idx_board_size_waist on public.board_size using btree (waist_width_mm) TABLESPACE pg_default;

create index IF not exists idx_board_size_weight on public.board_size using btree (rider_weight_min_lbs, rider_weight_max_lbs) TABLESPACE pg_default;

create index IF not exists idx_board_size_sidecut on public.board_size using btree (sidecut_radius_m) TABLESPACE pg_default;

create trigger populate_sidecut_radius_trigger BEFORE INSERT
or
update on board_size for EACH row
execute FUNCTION populate_sidecut_radius ();

create trigger update_board_size_updated_at BEFORE
update on board_size for EACH row
execute FUNCTION update_updated_at_column ();

-- Junction tables for board_size (must come after board_size)
create table public.board_size_binding_size (
  board_size_id integer not null,
  binding_size_id integer not null,
  constraint board_size_binding_size_pkey primary key (board_size_id, binding_size_id),
  constraint board_size_binding_size_binding_size_id_fkey foreign KEY (binding_size_id) references binding_size (id) on delete CASCADE,
  constraint board_size_binding_size_board_size_id_fkey foreign KEY (board_size_id) references board_size (id) on delete CASCADE
) TABLESPACE pg_default;

create table public.board_size_boot_size (
  board_size_id integer not null,
  boot_size_id integer not null,
  constraint board_size_boot_size_pkey primary key (board_size_id, boot_size_id),
  constraint board_size_boot_size_board_size_id_fkey foreign KEY (board_size_id) references board_size (id) on delete CASCADE,
  constraint board_size_boot_size_boot_size_id_fkey foreign KEY (boot_size_id) references boot_size (id) on delete CASCADE
) TABLESPACE pg_default;

-- views

CREATE OR REPLACE VIEW public.board_catalog with (security_invoker = on) AS
SELECT 
  bm.id,
  bm.model_name,
  bm.model_year,
  bm.gender,
  bm.msrp,
  bm.flex_rating,
  bm.source_url,
  bm.image_url,
  bm.created_at,
  bm.updated_at,
  -- Brand info
  b.name as brand_name,
  b.website_url as brand_url,
  -- Resolved standard values (not aliases)
  p.standard_name as profile,
  s.standard_name as shape,
  rt.standard_name as response_type,
  -- Aggregated arrays
  ARRAY_AGG(DISTINCT al.name) FILTER (WHERE al.name IS NOT NULL) as ability_levels,
  ARRAY_AGG(DISTINCT tt.name) FILTER (WHERE tt.name IS NOT NULL) as terrain_types
FROM board_model bm
LEFT JOIN brand b ON bm.brand_id = b.id
LEFT JOIN profile p ON bm.profile_id = p.id
LEFT JOIN shape s ON bm.shape_id = s.id
LEFT JOIN response_type rt ON bm.response_type_id = rt.id
LEFT JOIN board_model_ability_level bmal ON bm.id = bmal.board_model_id
LEFT JOIN ability_level al ON bmal.ability_level_id = al.id
LEFT JOIN board_model_terrain_type bmtt ON bm.id = bmtt.board_model_id
LEFT JOIN terrain_type tt ON bmtt.terrain_type_id = tt.id
GROUP BY 
  bm.id, bm.model_name, bm.model_year, bm.gender, bm.msrp, 
  bm.flex_rating, bm.source_url, bm.image_url, bm.created_at, bm.updated_at,
  b.name, b.website_url,
  p.standard_name,
  s.standard_name,
  rt.standard_name;

-- View: Board sizes with resolved data
CREATE OR REPLACE VIEW public.board_sizes_catalog with (security_invoker = on) AS
SELECT 
  bs.id,
  bs.board_model_id,
  bs.size_cm,
  bs.wide,
  bs.effective_edge_mm,
  bs.waist_width_mm,
  bs.tip_width_mm,
  bs.tail_width_mm,
  bs.running_length_mm,
  bs.sidecut_radius_m,
  bs.sidecut_entry_radius_m,
  bs.sidecut_focus_radius_m,
  bs.sidecut_exit_radius_m,
  bs.sidecut_depth_mm,
  bs.reference_stance_in,
  bs.min_stance_in,
  bs.max_stance_in,
  bs.setback_in,
  bs.insert_count,
  bs.rider_weight_min_lbs,
  bs.rider_weight_max_lbs,
  -- Aggregated recommended sizes
  ARRAY_AGG(DISTINCT boot.us_size) FILTER (WHERE boot.us_size IS NOT NULL) as recommended_boot_sizes,
  ARRAY_AGG(DISTINCT bind.size) FILTER (WHERE bind.size IS NOT NULL) as recommended_binding_sizes
FROM board_size bs
LEFT JOIN board_size_boot_size bsbs ON bs.id = bsbs.board_size_id
LEFT JOIN boot_size boot ON bsbs.boot_size_id = boot.id
LEFT JOIN board_size_binding_size bsbind ON bs.id = bsbind.board_size_id
LEFT JOIN binding_size bind ON bsbind.binding_size_id = bind.id
GROUP BY 
  bs.id, bs.board_model_id, bs.size_cm, bs.wide,
  bs.effective_edge_mm, bs.waist_width_mm, bs.tip_width_mm, bs.tail_width_mm,
  bs.running_length_mm, bs.sidecut_radius_m, bs.sidecut_entry_radius_m,
  bs.sidecut_focus_radius_m, bs.sidecut_exit_radius_m, bs.sidecut_depth_mm,
  bs.reference_stance_in, bs.min_stance_in, bs.max_stance_in, bs.setback_in,
  bs.insert_count, bs.rider_weight_min_lbs, bs.rider_weight_max_lbs;

-- View: Simple lookup tables (still useful for filters/facets)
CREATE OR REPLACE VIEW public.catalog_filters with (security_invoker = on) AS
SELECT 
  'ability_level' as filter_type,
  id,
  name as value,
  sort_order
FROM ability_level
UNION ALL
SELECT 
  'terrain_type' as filter_type,
  id,
  name as value,
  NULL as sort_order
FROM terrain_type
UNION ALL
SELECT 
  'profile' as filter_type,
  id,
  standard_name as value,
  NULL as sort_order
FROM profile
UNION ALL
SELECT 
  'shape' as filter_type,
  id,
  standard_name as value,
  NULL as sort_order
FROM shape
UNION ALL
SELECT 
  'response_type' as filter_type,
  id,
  standard_name as value,
  sort_order
FROM response_type
UNION ALL
SELECT 
  'brand' as filter_type,
  id,
  name as value,
  NULL as sort_order
FROM brand;