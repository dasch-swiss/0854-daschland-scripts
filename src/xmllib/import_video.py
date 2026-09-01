import pandas as pd
from dsp_tools.xmllib import (
    LicenseRecommended,
    Resource,
    create_list_from_input,
)

from src.folder_paths import PROCESSED_FOLDER, VIDEO_FOLDER


def main() -> list[Resource]:
    all_resources: list[Resource] = []

    # define dataframe
    video_df = pd.read_csv(PROCESSED_FOLDER / "Video.csv", dtype="str")

    # iterate through rows of dataframe:
    for _, row in video_df.iterrows():
        # define variables
        video_path = f"{VIDEO_FOLDER / row['File Name']}"
        authors = create_list_from_input(input_value=row["Authorship"], separator=",")
        authors_resource = create_list_from_input(input_value=row["Authorship Resource"], separator=",")

        # create resource, label and id
        resource = Resource.create_new(
            res_id=row["ID"],
            restype=":Video",
            label=row["Label"],
            authorship=authors_resource,
        )

        # add file to resource
        resource.add_file(
            video_path,
            license=LicenseRecommended.DSP.PUBLIC_DOMAIN,
            copyright_holder=row["Copyright"],
            authorship=authors,
        )

        # add properties to resource
        resource.add_simpletext("project-metadata:hasID", row["ID"])
        resource.add_time_optional("project-metadata:hasTimeStamp", row["Time Stamp"])
        resource.add_decimal_optional("project-metadata:hasFileSize", row["File Size"])
        resource.add_uri_optional(":hasWikidataLink", row["Wikidata Link"])
        resource.add_simpletext("project-metadata:hasFileName", row["File Name"])
        resource.add_richtext(":hasDescription", row["Description"])
        resource.add_textarea_optional(":hasCast", row["Cast"])

        # append resource to list
        all_resources.append(resource)

    return all_resources


if __name__ == "__main__":
    main()
