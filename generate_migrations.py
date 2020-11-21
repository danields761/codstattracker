import argparse
import re
from pathlib import Path
from typing import Callable, Iterable


def get_alembic_ini_path() -> Path:
    self_path = Path(__file__).parent.absolute()
    a_path = self_path / 'alembic.ini'
    if not a_path.is_file():
        raise Exception(
            'alembic.ini must be available and be in same dir as this script'
        )
    return a_path


def get_migrations_dir() -> Path:
    import configparser

    cfg_path = get_alembic_ini_path()
    with open(cfg_path, 'rt') as cfg_f:
        parser = configparser.ConfigParser()
        parser.read_file(cfg_f, str(cfg_path))
        assert parser.has_section(
            'alembic'
        ), '[alembic] section must be in file'
        m_dir = (
            cfg_path.parent
            / parser.get('alembic', 'script_location')
            / 'versions'
        )
        if not m_dir.is_dir():
            raise Exception(f'{m_dir} must be a directory')
        return m_dir


def list_migrations() -> list[tuple[str, str, Path]]:
    def inner() -> Iterable[tuple[str, str, Path]]:
        revision_re = re.compile(r'(\d+)_([\w_-]+).py')

        m_dir = get_migrations_dir()
        for file_name in m_dir.iterdir():
            match = revision_re.match(file_name.name)
            if not match:
                continue
            revision, name = match.groups()
            yield revision, name, file_name

    return sorted(list(inner()), key=lambda item: int(item[0]))


def get_alembic_main(alembic_executable: str) -> Callable:
    from subprocess import CalledProcessError, run

    def main(*args) -> str:
        new_args = [alembic_executable] + [str(arg) for arg in args]
        try:
            proc = run(new_args, capture_output=True, check=True)
        except CalledProcessError as err:
            print('Alembic error', err.stderr.decode())
            raise

        return proc.stdout.decode()

    return main


def generate_raw_migrations(
    migrations: list[tuple[str, str, Path]],
    alembic_executable: str,
    target_db_type: str,
) -> Iterable[tuple[int, str, str, str]]:
    alembic_main = get_alembic_main(alembic_executable)
    base_args = (
        '-c',
        str(get_alembic_ini_path()),
        '-x',
        f'db-type={target_db_type}',
    )

    revisions = [
        (prev_rev, rev, migration_name)
        for (prev_rev, _, _), (rev, migration_name, _) in zip(
            migrations, migrations[1:]
        )
    ]

    # Zero migrations
    first_revision, first_revision_name, _ = migrations[0]
    fr_up = alembic_main(*base_args, 'upgrade', first_revision, '--sql')
    fr_down = alembic_main(
        *base_args, 'downgrade', f'{first_revision}:-1', '--sql'
    )
    yield first_revision, first_revision_name, fr_up, fr_down

    for rev, next_rev, next_rev_name in revisions:
        up = alembic_main(*base_args, 'upgrade', f'{rev}:{next_rev}', '--sql')
        down = alembic_main(
            *base_args, 'downgrade', f'{next_rev}:{rev}', '--sql'
        )
        yield next_rev, next_rev_name, up, down


def write_raw_migrations(
    raw_migrations: Iterable[tuple[int, str, str, str]], dst_dir: Path
) -> None:
    for rev, name, up, down in raw_migrations:
        up_file = dst_dir / f'{rev}.{name}.up.sql'
        up_file.write_text(up)

        down_file = dst_dir / f'{rev}.{name}.down.sql'
        down_file.write_text(down)


def generate_migrations(alembic_executable: str, target_db_type: str, dst_dir: Path) -> None:
    assert dst_dir.is_dir(), 'Destination must be a directory'

    migrations = list_migrations()
    print(
        f'Collected {len(migrations)} migrations from {get_migrations_dir()}'
    )
    raw_migrations = generate_raw_migrations(
        migrations, alembic_executable, target_db_type
    )
    write_raw_migrations(raw_migrations, dst_dir)

    print(f'Migrations for {target_db_type} written into {dst_dir}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--alembic', default='alembic')
    parser.add_argument('db-type')
    parser.add_argument('destination-dir', type=Path)

    args = parser.parse_args()
    generate_migrations(
        args.alembic,
        args.__dict__['db-type'],
        args.__dict__['destination-dir'],
    )


if __name__ == '__main__':
    main()
