"""
 Copyright (c) 2023 Intel Corporation
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at
      http://www.apache.org/licenses/LICENSE-2.0
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""
import sys
from contextlib import contextmanager
from pathlib import Path

# pylint: disable=W1514
@contextmanager
def safe_open(file: Path, *args, **kwargs):
    """
    Safe function to open file and return a stream.

    For security reasons, should not follow symlinks. Use .resolve() on any Path
    objects before passing them here.

    :param file: The path to the file.
    :return: A file object.
    """
    if file.is_symlink():
        raise RuntimeError('File {} is a symbolic link, aborting.'.format(str(file)))
    with open(str(file), *args, **kwargs) as f:
        yield f


def is_windows():
    return "win32" in sys.platform


def is_linux():
    return "linux" in sys.platform
