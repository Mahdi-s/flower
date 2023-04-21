"""Functions to download and process CSV files."""


import os
import ssl
import tarfile
import urllib.request

import pandas as pd


def _download_file(url, filename):
    """Download the file and show a progress bar."""

    print(f"Downloading {url}...")
    retries = 3
    while retries > 0:
        try:
            with urllib.request.urlopen(
                url,
                context=ssl._create_unverified_context(),  # pylint: disable=protected-access
            ) as response, open(filename, "wb") as out_file:
                total_size = int(response.getheader("Content-Length"))
                block_size = 1024 * 8
                count = 0
                while True:
                    data = response.read(block_size)
                    if not data:
                        break
                    count += 1
                    out_file.write(data)
                    percent = int(count * block_size * 100 / total_size)
                    print(
                        f"\rDownloading: {percent}% [{count * block_size}/{total_size}]",
                        end="",
                    )
                print("\nDownload complete.")
        except Exception as error:  # pylint: disable=broad-except
            print(f"\nError occurred during download: {error}")
            retries -= 1
            if retries > 0:
                print(f"Retrying ({retries} retries left)...")
            else:
                print("Download failed.")
                raise error


def _extract_file(filename, extract_path):
    """Extract the contents and show a progress bar."""

    print(f"Extracting {filename}...")
    with tarfile.open(filename, "r:gz") as tar:
        members = tar.getmembers()
        total_files = len(members)
        current_file = 0
        for member in members:
            current_file += 1
            tar.extract(member, path=extract_path)
            percent = int(current_file * 100 / total_files)
            print(f"\rExtracting: {percent}% [{current_file}/{total_files}]", end="")
        print("\nExtraction complete.")


def _delete_file(filename):
    """Delete the downloaded file."""

    os.remove(filename)
    print(f"Deleted {filename}.")


def _csv_path_audio():
    """Change the path corespond to your actual path."""

    df_concat_train = None
    df_concat_dev = None
    df_concat_test = None
    for i in range(1983):
        df_train = pd.read_csv(f"./data/client_{i}/ted_train.csv")
        df_dev = pd.read_csv(f"./data/client_{i}/ted_dev.csv")
        df_test = pd.read_csv(f"./data/client_{i}/ted_test.csv")
        df_train["wav"] = df_train["wav"].str.replace(
            "path", "./data/audio/TEDLIUM_release-3/legacy/train/sph/"
        )
        df_dev["wav"] = df_dev["wav"].str.replace(
            "path", "./data/audio/TEDLIUM_release-3/legacy/train/sph/"
        )
        df_test["wav"] = df_test["wav"].str.replace(
            "path", "./data/audio/TEDLIUM_release-3/legacy/train/sph/"
        )
        df_train.to_csv(f"./data/client_{i}/ted_train.csv", index=False)
        df_dev.to_csv(f"./data/client_{i}/ted_dev.csv", index=False)
        df_test.to_csv(f"./data/client_{i}/ted_test.csv", index=False)
        if df_concat_train is None:
            df_concat_train = df_train
        else:
            df_concat_train = pd.concat([df_concat_train, df_train], ignore_index=True)
        if df_concat_dev is None:
            df_concat_dev = df_dev
        else:
            df_concat_dev = pd.concat([df_concat_dev, df_dev], ignore_index=True)
        if df_concat_test is None:
            df_concat_test = df_test
        else:
            df_concat_test = pd.concat([df_concat_test, df_test], ignore_index=True)

    df_concat_train.to_csv("./data/ted_train.csv", index=False)
    df_concat_dev.to_csv("./data/ted_dev.csv", index=False)
    df_concat_test.to_csv("./data/ted_test.csv", index=False)


if __name__ == "__main__":
    URL = (
        "https://projets-lium.univ-lemans.fr"
        "/wp-content/uploads/corpus/TED-LIUM/TEDLIUM_release-3.tgz"
    )
    FILENAME = "data/TEDLIUM_release-3.tgz"
    EXTRACT_PATH = "data/audio"

    if not os.path.exists(EXTRACT_PATH):
        try:
            _download_file(URL, FILENAME)
            _extract_file(FILENAME, EXTRACT_PATH)
        finally:
            _delete_file(FILENAME)

    _csv_path_audio()