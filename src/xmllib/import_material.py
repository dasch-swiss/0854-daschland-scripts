import pandas as pd
from dsp_tools.xmllib import LicenseRecommended, Resource, create_list_from_input

from src.folder_paths import OUTPUT_FOLDER, PROCESSED_FOLDER


def main() -> list[Resource]:
    all_resources: list[Resource] = []

    # define dataframe
    material_df = pd.read_csv(PROCESSED_FOLDER / "Material.csv", dtype="str")

    # iterate through rows of dataframe:
    for _, row in material_df.iterrows():
        if row["File Name"].lower().endswith(".csv"):
            material_path = f"{PROCESSED_FOLDER / row['File Name']}"
        else:
            material_path = f"{OUTPUT_FOLDER / row['File Name']}"

        authors = create_list_from_input(input_value=row["Authorship"], separator=",")
        authors_resource = create_list_from_input(input_value=row["Authorship Resource"], separator=",")

        # create resource, label and id
        resource = Resource.create_new(
            res_id=row["ID"],
            restype="project-metadata:Material",
            label=row["File Name"],
            authorship=authors_resource,
        )

        # add file to resource
        resource.add_file(
            material_path, license=LicenseRecommended.CC.BY, copyright_holder=row["Copyright"], authorship=authors
        )

        # add properties to resource
        resource.add_simpletext("project-metadata:hasID", row["ID"])
        resource.add_simpletext("project-metadata:hasFileName", row["File Name"])
        resource.add_richtext("project-metadata:hasFileDescription", row["Description"])
        resource.add_time_optional("project-metadata:hasTimeStamp", row["Time Stamp"])
        resource.add_decimal_optional("project-metadata:hasFileSize", row["File Size"])
        # append resource to list
        all_resources.append(resource)

    return all_resources


if __name__ == "__main__":
    main()
