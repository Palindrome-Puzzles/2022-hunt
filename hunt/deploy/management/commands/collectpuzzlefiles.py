import pathlib, re, urllib.parse

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings

from hunt.app.core.assets.refs import hash_asset_type, from_bytes, to_bytes
from hunt.data_loader.puzzle import get_all_puzzle_data
from hunt.data_loader.round import get_all_round_data
from hunt.data_loader.chunks import get_all_shared_chunks
from hunt.data_loader.auxiliary import get_all_auxiliary_files

from ._common import confirm_command

_PUZZLE_FILES_TO_SKIP = [
    pathlib.PurePath('config.json'),
    pathlib.PurePath('metadata.json'),
    pathlib.PurePath('hints.json')
]

_REWRITE_CHUNKS_PATTERN = re.compile(r"""\"/(?P<static_path>chunks/chunk-[^."]+.js)\"""")

_SKIP_EXTENSIONS = ('.tmpl', '.ts', '.scss', '.py')

_GZIP_EXTENSIONS = ('.html', '.js', '.css')
_GZIP_SUBFOLDER = 'gzip'
_NOT_GZIP_SUBFOLDER = 'not-gzip'

class Command(BaseCommand):
    help = 'Collects all puzzle and round files to the static temp directory, sharded by gzippable and not gzippable'

    def add_arguments(self, parser):
        parser.add_argument(
            '--noinput', action='store_false', dest='interactive',
            help="Do NOT prompt the user for input of any kind.",
        )
        parser.add_argument(
            '--gzip-files', action='store', dest='gzip_files',
            default='true', help="Whether to split some files out as gzippable.",
        )

    def handle(self, *args, **options):
        if options['interactive'] and not confirm_command('This will first delete all files from the static temp directory!'):
            return

        gzip_files = options['gzip_files'] == 'true'

        call_command('collectstatic', interactive=False, clear=True)
        call_command('removepuzzlefiles', interactive=False)

        _collect_shared_chunks(debug=options['interactive'], gzip_files=gzip_files)
        _collect_static(debug=options['interactive'], gzip_files=gzip_files)
        _collect_static_temp(
            get_all_puzzle_data(), 'puzzle', debug=options['interactive'], gzip_files=gzip_files)
        _collect_static_temp(
            get_all_round_data(), 'round', debug=options['interactive'], gzip_files=gzip_files)
        _collect_static_temp(
            get_all_auxiliary_files(), 'auxiliary', debug=options['interactive'], gzip_files=gzip_files)

def _collect_static_temp(data_path, asset_type, *, debug, gzip_files):
    gzip_static_dest_path = pathlib.Path(settings.HUNT_ASSETS_TEMP_FOLDER, _GZIP_SUBFOLDER, settings.HUNT_ASSETS_STATIC_PREFIX)
    not_gzip_static_dest_path = pathlib.Path(settings.HUNT_ASSETS_TEMP_FOLDER, _NOT_GZIP_SUBFOLDER, settings.HUNT_ASSETS_STATIC_PREFIX)

    count = 0
    for path in data_path.rglob('*'):
        if path.is_dir():
            continue

        if any(path.name.endswith(raw_ext) for raw_ext in _SKIP_EXTENSIONS):
            continue

        relative_path = path.relative_to(data_path)
        relative_path_parts = relative_path.parts
        assert len(relative_path_parts) >= 2

        asset_url = relative_path_parts[0]

        variant = asset_type
        resource_path_parts = relative_path_parts[1:]
        is_gzippable = any(path.name.endswith(raw_ext) for raw_ext in _GZIP_EXTENSIONS)
        should_gzip = is_gzippable and gzip_files

        if resource_path_parts[0] == 'solution':
            variant = 'solution'
            resource_path_parts = resource_path_parts[1:]
        elif asset_type == 'puzzle' and resource_path_parts[0] == 'posthunt':
            variant = 'posthunt'
            resource_path_parts = resource_path_parts[1:]
        elif resource_path_parts[0] == '__build':
            continue

        assert len(resource_path_parts)

        resource_path = pathlib.PurePath(*resource_path_parts)
        if not _should_copy_file(
            asset_type=asset_type, variant=variant, resource_path=resource_path):
            continue

        key = hash_asset_type(asset_type, asset_url, variant)
        if debug:
            print(f'Processing {asset_type} {asset_url}{" solution" if variant else ""}: {resource_path} (key={key})')

        base_path = gzip_static_dest_path if should_gzip else not_gzip_static_dest_path
        dest = base_path.joinpath(key, resource_path)
        dest.parent.mkdir(parents=True, exist_ok=True)

        assert not dest.exists()
        content = path.read_bytes()
        rewritten_content = _maybe_rewrite(path.name, content)
        dest.write_bytes(rewritten_content)
        count += 1
    print(f'Processed {count} {asset_type} files')

def _collect_shared_chunks(*, debug, gzip_files):
    data_path = get_all_shared_chunks()

    gzip_static_dest_path = pathlib.Path(settings.HUNT_ASSETS_TEMP_FOLDER, _GZIP_SUBFOLDER, settings.HUNT_DATA_PACKAGE_CHUNKS)
    not_gzip_static_dest_path = pathlib.Path(settings.HUNT_ASSETS_TEMP_FOLDER, _NOT_GZIP_SUBFOLDER, settings.HUNT_DATA_PACKAGE_CHUNKS)
    base_path = gzip_static_dest_path if gzip_files else not_gzip_static_dest_path

    count = 0
    for path in data_path.rglob('*'):
        relative_path = path.relative_to(data_path)
        dest = base_path.joinpath(relative_path)
        dest.parent.mkdir(parents=True, exist_ok=True)

        assert not dest.exists()
        content = path.read_bytes()
        rewritten_content = _maybe_rewrite(path.name, content)
        dest.write_bytes(rewritten_content)
        count += 1
    print(f'Processed {count} chunks')

def _collect_static(*, debug, gzip_files):
    data_path = pathlib.Path(settings.STATIC_ROOT)
    gzip_static_dest_path = pathlib.Path(settings.HUNT_ASSETS_TEMP_FOLDER, _GZIP_SUBFOLDER)
    not_gzip_static_dest_path = pathlib.Path(settings.HUNT_ASSETS_TEMP_FOLDER, _NOT_GZIP_SUBFOLDER)

    count = 0
    for path in data_path.rglob('*'):
        if path.is_dir():
            continue

        is_gzippable = any(path.name.endswith(raw_ext) for raw_ext in _GZIP_EXTENSIONS)
        should_gzip = is_gzippable and gzip_files
        base_path = gzip_static_dest_path if should_gzip else not_gzip_static_dest_path

        relative_path = path.relative_to(data_path)
        dest = base_path.joinpath(relative_path)
        dest.parent.mkdir(parents=True, exist_ok=True)

        assert not dest.exists()
        content = path.read_bytes()
        dest.write_bytes(content)
        count += 1
    print(f'Processed {count} assets')

def _should_copy_file(*, asset_type, variant, resource_path):
    # Note: we could skip index.html/style.css/round_common.css (or
    # their compiled versions) as these are served by Django. However, it
    # doesn't hurt to deploy them, and deploying could be useful. For example,
    # if index.html embeds another HTML file in an iframe, then that iframed
    # file could reuse style.css.
    if asset_type == 'puzzle' and variant == 'puzzle':
        return resource_path not in _PUZZLE_FILES_TO_SKIP
    return True

def _maybe_rewrite(name, content):
    # Rewrite JS references to chunks. esbuild is annoying and won't let me use
    # absolute paths to chunks. So when we use static serving, we need to rewrite
    # them ourselves.
    if name.endswith('.js'):
        return to_bytes(_REWRITE_CHUNKS_PATTERN.sub(_replace_js_chunk_refs, from_bytes(content)))
    return content

def _replace_js_chunk_refs(match):
    static_root = settings.STATIC_URL
    named_matches = match.groupdict()
    static_path = named_matches['static_path']
    return f'"{urllib.parse.urljoin(static_root, static_path)}"'
