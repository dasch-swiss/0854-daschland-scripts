import pandas as pd
from dsp_tools.xmllib import (
    LicenseRecommended,
    Resource,
    create_list_from_input,
)

from src.folder_paths import ARCHIVE_FOLDER, PROCESSED_FOLDER


def main() -> list[Resource]:
    all_resources: list[Resource] = []

    # define dataframe
    archive_df = pd.read_csv(PROCESSED_FOLDER / "Archive.csv")

    # iterate through rows of dataframe:
    for _, row in archive_df.iterrows():
        # define variables
        archive_path = f"{ARCHIVE_FOLDER / row['File Name']}"

        authors = create_list_from_input(input_value=row["Authorship"], separator=",")
        authors_resource = create_list_from_input(input_value=row["Authorship Resource"], separator=",")

        # create resource, label and id
        resource = Resource.create_new(
            res_id=row["ID"],
            restype="project-metadata:Archive",
            label=row["File Name"],
            authorship=authors_resource,
        )

        # add file to resource
        resource.add_file(
            filename=archive_path,
            license=LicenseRecommended.CC.BY,
            copyright_holder=row["Copyright"],
            authorship=authors,
        )

        # add properties to resource
        resource.add_simpletext("project-metadata:hasID", row["ID"])
        resource.add_richtext("project-metadata:hasFileDescription", row["Description"])
        resource.add_simpletext("project-metadata:hasFileName", row["File Name"])
        resource.add_time_optional("project-metadata:hasTimeStamp", row["Time Stamp"])
        resource.add_decimal_optional("project-metadata:hasFileSize", row["File Size"])
        resource.add_simpletext("project-metadata:hasCopyrightResource", "DaSCH")
        resource.add_list("project-metadata:hasLicenseResource", "License", "LIC_002")

        # append resource to list
        all_resources.append(resource)

    return all_resources


if __name__ == "__main__":
    main()
