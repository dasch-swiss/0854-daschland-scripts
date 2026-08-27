import pandas as pd
from dsp_tools.xmllib import Resource, create_list_from_input

from src.folder_paths import PROCESSED_FOLDER


def main() -> list[Resource]:
    all_resources: list[Resource] = []

    # define dataframe
    location_df = pd.read_csv(PROCESSED_FOLDER / "Location.csv", dtype="str")

    # iterate through rows of dataframe:
    for _, row in location_df.iterrows():
        # define variables
        resource_id = row["ID"]
        resource_label = row["Name"]
        descriptions = [
            row["Description EN"],
            row["Description DE"],
            row["Description FR"],
            row["Description IT"],
        ]
        descriptions = [description for description in descriptions if pd.notna(description)]
        image_ids = create_list_from_input(row["Image ID"], separator=",")
        authors_resource = create_list_from_input(input_value=row["Authorship Resource"], separator=",")

        location_type_to_restype_lookup = {
            "Real World": ":LocationRealWorld",
            "Wonderland": ":LocationWonderland",
        }

        restype_found = location_type_to_restype_lookup.get(row["Location Type List"])
        if restype_found is not None:
            restype = restype_found
        else:
            restype = ":Location"

        # create resource, label and id
        resource = Resource.create_new(
            res_id=resource_id,
            restype=restype,
            label=resource_label,
            authorship=authors_resource,
        )

        # add properties to resource
        resource.add_simpletext("project-metadata:hasID", resource_id)
        resource.add_simpletext(":hasName", row["Name"])
        resource.add_richtext_multiple(prop_name=":hasDescription", values=descriptions)
        resource.add_link_multiple(":linkToImage", image_ids)
        resource.add_geoname_optional(":hasGeoname", row["Geoname ID"])
        resource.add_uri_optional(":hasWikidataLink", row["Wikidata Link"])

        # append resource to list
        all_resources.append(resource)

    return all_resources


if __name__ == "__main__":
    main()
