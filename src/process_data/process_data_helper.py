import os
import pathlib
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import pandas as pd
from exiftool import ExifToolHelper
from PIL import Image
from PIL.ExifTags import TAGS

from src.folder_paths import PROCESSED_FOLDER, RAW_FOLDER


def update_spreadsheet_df(class_name: str) -> None:
    df = pd.read_excel(RAW_FOLDER / f"{class_name}.xlsx", dtype="str")
    df_cleaned = df.dropna(how="all")
    _write_df_to_csv(df_cleaned, PROCESSED_FOLDER / f"{class_name}.csv")


def update_multimedia_df(
    class_name: str, multimedia_folder: pathlib.Path, alternative_column: Optional[str] = None
) -> None:
    df = pd.read_excel(RAW_FOLDER / f"{class_name}.xlsx", dtype="str")
    df_cleaned = df.dropna(how="all")
    if alternative_column is None:
        updated_df = _add_absolute_file_paths(df_cleaned, multimedia_folder)
    else:
        updated_df = _add_absolute_file_paths_with_multiple_folders(df_cleaned, multimedia_folder)
    updated_df = _add_exif_data_to_df(updated_df)
    # remove the temporary column as we do not want to save absolute paths in the file
    updated_df.pop("AbsoluteFilePath")
    _write_df_to_csv(df=updated_df, path=PROCESSED_FOLDER / f"{class_name}.csv")


def _add_absolute_file_paths(df: pd.DataFrame, multimedia_folder: pathlib.Path) -> pd.DataFrame:
    # Ensure you're working with a copy of the DataFrame
    df_copy = df.copy()
    # Construct a Series of Path objects
    df_copy["AbsoluteFilePath"] = df_copy["File Name"].apply(
        lambda x: str(multimedia_folder / x)
    )  # Now apply your functions to the Series
    return df_copy


def _add_absolute_file_paths_with_multiple_folders(
    df: pd.DataFrame, generic_multimedia_folder: pathlib.Path
) -> pd.DataFrame:
    df_copy = df.copy()
    df_copy["Multimedia Folder with path"] = df_copy["Multimedia Folder"].apply(lambda x: generic_multimedia_folder / x)
    for i, row in df_copy.iterrows():
        df_copy.loc[i, "AbsoluteFilePath"] = row["Multimedia Folder with path"] / row["File Name"]
    df_copy.pop("Multimedia Folder with path")
    return df_copy


def _add_exif_data_to_df(df: pd.DataFrame) -> pd.DataFrame:
    df_copy = df.copy()
    df_copy["Time Stamp"] = df_copy["AbsoluteFilePath"].apply(get_media_file_creation_timestamp)
    df_copy["File Size"] = df_copy["AbsoluteFilePath"].apply(get_media_file_size)
    return df_copy


def _write_df_to_csv(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False)


def get_media_file_creation_timestamp(file_path: str | pathlib.Path) -> str | None:
    file_path_str = str(file_path)
    image_suffixes = ["jpg", "jpeg", "png"]
    suffix = file_path_str.rsplit(".", 1)[-1]
    if suffix in image_suffixes:
        return _get_image_creation_time(file_path)

    return _get_generic_media_file_creation_timestamp(file_path)


def _get_generic_media_file_creation_timestamp(file_path: str | pathlib.Path) -> str | None:
    try:
        with ExifToolHelper() as et:
            metadata_list = et.get_metadata(file_path)
            if not metadata_list:
                return None

            metadata = metadata_list[0]
            # Loop through metadata to find the first valid CreateDate
            for key, value in metadata.items():
                if key.endswith("CreateDate"):
                    return _convert_media_creation_time_to_dsp_time(value)
            return None
    except Exception as e:  # noqa: BLE001 (Do not catch blind exceptions)
        print(f"Error processing file {file_path}: {e}")
        return None


def _get_image_creation_time(image_path: str | pathlib.Path) -> str | None:
    image_path = os.path.expanduser(image_path)
    # convert image_path into pathlib object:
    image_path_conform = Path(image_path)

    # Open the image file
    image = Image.open(image_path_conform)

    # Extract EXIF data
    exif_data: dict[int, Any] = image._getexif()  # type: ignore[attr-defined]
    # If no EXIF data found
    if not exif_data:
        return None

    date_time_raw = _get_time_from_exif_data(exif_data)
    if not date_time_raw:
        return None

    # convert the creation time to CE time
    time_conform = _convert_creation_time_to_dsp_time(str(date_time_raw))
    if time_conform:
        return time_conform
    else:
        return None


def _get_time_from_exif_data(exif_data: dict[int, str]) -> str | None:
    # Loop through the EXIF data to find the creation time
    for tag, value in exif_data.items():
        tag_name = str(TAGS.get(tag, tag))  # Convert to string
        if tag_name == "DateTimeOriginal" or "DateTime" in tag_name:
            return value
        else:
            continue
    return None


def _convert_creation_time_to_dsp_time(time: str) -> str | None:
    input_format = "%Y:%m:%d %H:%M:%S"
    output_format = "%Y-%m-%dT%H:%M:%S-00:00"
    try:
        time_to_convert = datetime.strptime(time, input_format)
        return time_to_convert.strftime(output_format)
    except ValueError:
        return None


def _convert_media_creation_time_to_dsp_time(time: str) -> str | None:
    # Define the input date format

    # Parse the date string into a datetime object
    date_formats = ["%Y:%m:%d %H:%M:%SZ", "%Y:%m:%dT%H:%M:%Sz", "%Y:%m:%d %H:%M:%S"]
    output_format = "%Y-%m-%dT%H:%M:%S-00:00"

    for date_format in date_formats:
        try:
            time_to_convert = datetime.strptime(time, date_format)
            return time_to_convert.strftime(output_format)
        except ValueError:
            continue
    return None


def get_media_file_size(file_path: str) -> Optional[float]:
    try:
        with ExifToolHelper() as et:
            metadata_list = et.get_metadata(file_path)
            if metadata_list:
                # Extract the first available size field (e.g., File:FileSize)
                file_size = next((value for key, value in metadata_list[0].items() if key.endswith("Size")), None)
                if file_size:
                    # Convert and round to 3 decimal places
                    return round(_convert_bytes_to_mb(file_size), 1)
            return None
    except Exception as e:  # noqa: BLE001
        print(f"Error reading metadata: {e}")
        return None


def _convert_bytes_to_mb(bytes_size: int) -> float:
    # 1 MB = 1024 * 1024 bytes
    megabytes_size = bytes_size / (1024 * 1024)
    return megabytes_size
