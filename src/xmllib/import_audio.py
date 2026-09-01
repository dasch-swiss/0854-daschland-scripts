import pandas as pd
from dsp_tools.xmllib import Resource, create_list_from_input, find_license_in_string

from src.folder_paths import AUDIO_FOLDER, PROCESSED_FOLDER


def main() -> list[Resource]:
    all_resources: list[Resource] = []

    # define dataframe
    audio_df = pd.read_csv(PROCESSED_FOLDER / "Audio.csv", dtype="str")

    # iterate through rows of dataframe:
    for _, row in audio_df.iterrows():
        # define variables
        audio_path = f"{AUDIO_FOLDER / row['File Name']}"
        authors = create_list_from_input(row["Authorship"], separator=", ")
        authors_resource = create_list_from_input(row["Authorship Resource"], separator=", ")
        file_license = find_license_in_string(row["License List"])
        # create resource, label and id
        resource = Resource.create_new(
            res_id=row["ID"],
            restype=":Audio",
            label=row["Name"],
            authorship=authors_resource,
        )

        # add file to resource
        resource.add_file(
            filename=audio_path,
            license=file_license,
            copyright_holder=row["Copyright"],
            authorship=authors,
        )

        # add properties to resource
        resource.add_simpletext("project-metadata:hasID", row["ID"])
        resource.add_time_optional("project-metadata:hasTimeStamp", row["Time Stamp"])
        resource.add_decimal_optional("project-metadata:hasFileSize", row["File Size"])
        resource.add_simpletext("project-metadata:hasFileName", row["File Name"])
        resource.add_richtext(":hasDescription", row["Description"])
        resource.add_textarea_optional(":hasCast", row["Cast"])

        # append resource to list
        all_resources.append(resource)

    return all_resources


if __name__ == "__main__":
    main()
