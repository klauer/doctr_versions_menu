"""Implementation of the versions-data collection."""
import logging
import re
from pathlib import Path

import jinja2
from packaging.version import parse as parse_version

from .folder_spec import resolve_folder_spec
from .groups import get_groups


def get_version_data(
    *,
    hidden=None,
    sort_key=None,
    suffix_latest,
    versions_spec,
    latest_spec,
    warnings,
    label_specs,
    downloads_file
):
    """Get the versions data, to be serialized to json."""
    if hidden is None:
        hidden = []
    if sort_key is None:
        sort_key = parse_version

    folders = sorted(
        [
            str(f)
            for f in Path().iterdir()
            if (
                f.is_dir()
                and not str(f).startswith('.')
                and not str(f).startswith('_')
                and str(f) not in hidden
            )
        ]
    )

    groups = get_groups(folders)

    labels = {}
    for (spec, template_str) in label_specs:
        label_folders = resolve_folder_spec(spec, groups)
        for folder in label_folders:
            label_template = jinja2.Environment().from_string(template_str)
            labels[folder] = label_template.render(folder=folder)
    for folder in folders:
        if folder not in labels:
            labels[folder] = folder

    try:
        latest_release = resolve_folder_spec(latest_spec, groups)[-1]
        labels[latest_release] += suffix_latest
    except IndexError:
        latest_release = None

    if 'outdated' not in warnings:
        warnings['outdated'] = '(<releases> < ' + str(latest_release) + ')'
        # spec '(<releases> < None) is an empty list
    if 'unreleased' not in warnings:
        warnings['unreleased'] = '<branches>, <local-releases>'
    if 'prereleased' not in warnings:
        warnings['prereleased'] = '<pre-releases>'
    versions = resolve_folder_spec(versions_spec, groups)
    versions = list(reversed(versions))  # newest first
    version_data = {
        # list of *all* folders
        'folders': folders,
        #
        # folder => labels for every folder in "Versions"
        'labels': labels,
        #
        # list folders that appear in "Versions"
        'versions': versions,
        #
        # list of folders that do not appear in "Versions"
        'hidden': hidden,
        #
        # map of folders to warning labels
        'warnings': {f: [] for f in folders},
        #
        # the latest stable release folder
        'latest_release': latest_release,
        #
        # folder => list of (label, file)
        'downloads': {
            folder: _find_downloads(folder, downloads_file)
            for folder in folders
        },
    }

    for (name, warning_spec) in warnings.items():
        warning_folders = resolve_folder_spec(warning_spec, groups)
        for folder in version_data['warnings'].keys():
            if folder in warning_folders:
                version_data['warnings'][folder].append(name)

    return version_data


def _find_downloads(folder, downloads_file):
    """Find artifact links in downloads_file file.

    The `downloads_file` should be created during the build procedure (on
    Travis).  If no `downloads_file` exists, return an empty list.

    Each line in the `downloads_file` should have the form ``[label]: url``.
    For backwards compatibility, having only the url is also acceptable. In
    this case, the label is derived from the file extension.
    """
    logger = logging.getLogger(__name__)
    downloads = []
    rx_line = re.compile(r'^\[(?P<label>.*)\]:\s*(?P<url>.*)$')
    rx_url = re.compile(r'^(\w+:/)?/')  # /... or http://...
    try:
        downloads_file = Path(folder) / downloads_file
        with downloads_file.open() as in_fh:
            logger.debug("Processing downloads_file %s", downloads_file)
            for line in in_fh:
                match = rx_line.match(line)
                if match:
                    url = match.group('url')
                    label = match.group('label')
                else:
                    logger.warning(
                        "Invalid line %r in %s: does not match '[label]: url'",
                        line.strip(),
                        downloads_file,
                    )
                    url = line.strip()
                    label = url.split(".")[-1].lower()
                if not rx_url.match(url):
                    logger.error("INVALID URL: %s", url)
                    logger.warning(
                        "Skipping invalid URL %r (must be absolute path or "
                        "external URL)",
                        url,
                    )
                    continue
                logger.debug(
                    "For %s, download link %r => %r", folder, label, url
                )
                downloads.append((label, url))
    except IOError:
        logger.warning("folder '%s' contains no %s", folder, downloads_file)
    return downloads
