begin;

create table pastes(
    shortlink char(8) not null primary key,
    paste_content_link text not null,
    expired boolean not null,
    expires_at timestamptz,
    created_at timestamptz not null,
    updated_at timestamptz
);

commit;
