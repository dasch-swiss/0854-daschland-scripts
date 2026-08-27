import pandas as pd
from dsp_tools.xmllib import (
    LicenseRecommended,
    Resource,
    create_list_from_input,
    find_dates_in_string,
)

from src.folder_paths import PROCESSED_FOLDER


def main() -> list[Resource]:
    all_resources: list[Resource] = []

    # define dataframe
    book_df = pd.read_csv(PROCESSED_FOLDER / "BookCover.csv", dtype="str")

    # iterate through rows of dataframe:
    for _, row in book_df.iterrows():
        # define variables
        authors = create_list_from_input(input_value=row["Authorship"], separator=",")
        authors_resource = create_list_from_input(input_value=row["Authorship Resource"], separator=",")
        copyright_stripped = row["Copyright"].split("\n")
        copyright_stripped = [c.strip() for c in copyright_stripped if c.strip()]
        copyright_string = " ".join(copyright_stripped)
        date_published = find_dates_in_string(row["Date Published"])
        # create resource, label and id
        resource = Resource.create_new(
            res_id=row["ID"],
            restype=":BookCover",
            label=row["Label"],
            authorship=authors_resource,
        )

        # add properties to resource
        resource.add_iiif_uri(
            row["URI"],
            license=LicenseRecommended.DSP.PUBLIC_DOMAIN,
            copyright_holder=copyright_string,
            authorship=authors,
        )
        resource.add_simpletext("project-metadata:hasID", row["ID"])
        resource.add_richtext(":hasDescription", row["Description"])
        resource.add_simpletext("project-metadata:hasCopyrightResource", "DaSCH")
        resource.add_list("project-metadata:hasLicenseResource", "License", "LIC_002")
        resource.add_uri(":hasUrl", row["Source"])
        resource.add_date_multiple(":hasDate", date_published)

        # append resource to list
        all_resources.append(resource)

    return all_resources


if __name__ == "__main__":
    main()
