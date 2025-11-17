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
  description text null,
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
  description text null,
  created_at timestamp with time zone null default now(),
  constraint response_type_pkey primary key (id),
  constraint response_type_standard_name_key unique (standard_name)
) TABLESPACE pg_default;

create table public.shape (
  id serial not null,
  standard_name character varying(50) not null,
  description text null,
  created_at timestamp with time zone null default now(),
  constraint shape_pkey primary key (id),
  constraint shape_standard_name_key unique (standard_name)
) TABLESPACE pg_default;

create table public.terrain_type (
  id serial not null,
  name character varying(50) not null,
  description text null,
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
  constraint board_model_shape_id_fkey foreign KEY (shape_id) references shape (id) on update CASCADE on delete set null,
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

create table public.board_model_shape (
  board_model_id integer not null,
  shape_id integer not null,
  constraint board_model_shape_pkey primary key (board_model_id, shape_id),
  constraint board_model_shape_board_model_id_fkey foreign KEY (board_model_id) references board_model (id) on delete CASCADE,
  constraint board_model_shape_shape_id_fkey foreign KEY (shape_id) references shape (id) on delete CASCADE
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