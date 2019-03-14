#!/usr/bin/python3

try:
  import argparse
  optparse = False
except ImportError:
  from optparse import OptionParser
  optparse = True
import csv
import glob
import hashlib
import locale
import os
import shutil
import io
import sys
import urllib.request
import time
from tqdm import tqdm  
chromium_url = "https://commondatastorage.googleapis.com/chromium-browser-official/"

chromium_root_dir = "."
version_string = "stable"

name = 'Chromium Latest (biswasab/chromium)'
script_version = 1.0
my_description = '{0} {1}'.format(name, script_version)

class TqdmUpTo(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
         if tsize is not None:
             self.total = tsize
         self.update(b * bsize - self.n)
       
    
    
# Get the latest version from omahaproxy
def check_omahaproxy(channel="stable"):

  version = 0
  status_url = "https://omahaproxy.appspot.com/all?os=linux&channel=" + channel
  with urllib.request.urlopen(status_url) as url:
    status_dump = url.read().decode('utf-8')
   
  status_list = io.StringIO(status_dump)
  status_reader = list(csv.reader(status_list, delimiter=','))
  linux_channels = [s for s in status_reader if "linux" in s]
  linux_channel = [s for s in linux_channels if channel in s]
  version = linux_channel[0][2]

  if version == 0:
    print(f"Couldn't find the latest {channel} build version")
    sys.exit(1)
  else:
    print(f'Latest Chromium Version on {channel} is {version}')
    return version
    
# DOWNLOAD FILE AND COMPARE HASHES-----------------------
def download_file_and_compare_hashes(file_to_download):

  hashes_file = '%s.hashes' % file_to_download
    # Let's make sure we haven't already downloaded it.
  tarball_local_file = "%s/%s" % (chromium_root_dir, file_to_download)
  if os.path.isfile(tarball_local_file):
    print (f"{file_to_download} already exists!")
  else:
    path = '%s%s' % (chromium_url, file_to_download)
    print (f"Downloading {file_to_download}")
    # Use tqdm
    with TqdmUpTo(unit='B', unit_scale=True, miniters=1,
              desc=path.split('/')[-1]) as t:
      info=urllib.request.urlretrieve(path, tarball_local_file, reporthook=t.update_to)[1] #info info=
    urllib.request.urlcleanup()
    print("")
    if (info["Content-Type"] != "application/x-tar"):
      print (f'Chromium tarballs for {file_to_download} are not on servers.' )
      remove_file_if_exists (file_to_download)
      sys.exit(1)

  hashes_local_file = "%s/%s" % (chromium_root_dir, hashes_file)
  if not os.path.isfile(hashes_local_file):
    path = '%s%s' % (chromium_url, hashes_file)
    print (f"Downloading hashes ...")
    with TqdmUpTo(unit='B', unit_scale=True, miniters=1,
              desc=path.split('/')[-1]) as t:
      info=urllib.request.urlretrieve(path, hashes_local_file, reporthook=t.update_to)[1]
        # info=
      urllib.request.urlcleanup()
    print ("")

  if os.path.isfile(hashes_local_file):
    with open(hashes_local_file, "r") as input_file:
      while True:
        hash_line = input_file.readline().split()
        if len(hash_line) == 0:
          print (f"Cannot compare SHA512 hash for {file_to_download}!"  )
        if hash_line[0] == 'sha512':
          sha512sum = hash_line[1]
          break
      sha512 = hashlib.sha512()
      with open(tarball_local_file, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
          sha512.update(block)
        if (sha512sum == sha512.hexdigest()):
          print (f"SHA512 matches for {file_to_download}!")
          remove_file_if_exists(hashes_file)
        else:
          print (f"SHA512 mismatch for {file_to_download}!")
          remove_file_if_exists(hashes_file)
          remove_file_if_exists(file_to_download)
          sys.exit(1)
  else:
    print (f"Cannot compare hashes for {file_to_download}!")
    
def download_version(version):

  download_file_and_compare_hashes ('chromium-%s.tar.xz' % version)

  if (args.tests):
    download_file_and_compare_hashes ('chromium-%s-testdata.tar.xz' % version)


def remove_file_if_exists(filename):

  filepath = "%s/%s" % (chromium_root_dir, filename)
  if os.path.isfile(filepath):
    try:
      os.remove(filepath)
    except Exception:
      pass
      
# This is where the magic happens
if __name__ == '__main__':
# Locale magic
  locale.setlocale(locale.LC_ALL, '')
  # Create the parser object
  if optparse:
    parser = OptionParser(description=my_description)
    parser_add_argument = parser.add_option
  else:
    parser = argparse.ArgumentParser(description=my_description)
    parser_add_argument = parser.add_argument
    
    parser.add_argument(
      'work_dir', type=str, nargs='?',
      help='Root of the working directory (default: current working directory)')
    parser_add_argument(
      '--beta', action='store_true',
      help='Get the latest beta Chromium source')
    parser_add_argument(
      '--dev', action='store_true',
      help='Get the latest dev Chromium source')
    parser_add_argument(
      '--stable', action='store_true',
      help='Get the latest stable Chromium source')
    parser_add_argument(
      '--tests', action='store_true',
      help='Get the additional data for running tests')
    parser_add_argument(
      '--version',
      help='Download a specific version of Chromium')
    # Parse the args
  if optparse:
    args, options = parser.parse_args()
  else:
    args = parser.parse_args()

  if args.work_dir:
    chromium_root_dir = args.work_dir

  if args.stable:
    version_string = "stable"
  elif args.beta:
    version_string = "beta"
  elif args.dev:
    version_string = "dev"
  elif (not (args.stable or args.beta or args.dev)):
    if (not args.version):
      print( 'No version specified, downloading STABLE')
  chromium_version = args.version if args.version else check_omahaproxy(version_string)
  latest = 'chromium-%s.tar.xz' % chromium_version
  download_version(chromium_version)
  print("Finished!") 
