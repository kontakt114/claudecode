create table if not exists leads (
  id uuid primary key default gen_random_uuid(),
  email text not null,
  insight_headline text,
  created_at timestamptz not null default now()
);
