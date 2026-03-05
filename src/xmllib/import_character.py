import pandas as pd
from dsp_tools.xmllib import (
    ListLookup,
    Resource,
    create_footnote_string,
    create_list_from_input,
    create_standoff_link_to_uri,
    get_list_nodes_from_string_via_list_name,
    is_nonempty_value,
)

from src.folder_paths import OUTPUT_FOLDER, PROCESSED_FOLDER
from src.helpers.helper import select_footnote_text


def main() -> list[Resource]:
    all_resources: list[Resource] = []

    # define json file path
    path_to_json = OUTPUT_FOLDER / "daschland.json"

    # define dataframe
    character_df = pd.read_csv(PROCESSED_FOLDER / "Character.csv", dtype="str")

    # create list mapping
    list_lookup = ListLookup.create_new(
        project_json_path=path_to_json,
        language_of_label="en",
        default_ontology="daschland",
    )

    # iterate through rows of dataframe:
    for _, row in character_df.iterrows():
        # define variables
        names = {row["Name EN"], row["Name DE"], row["Name FR"], row["Name IT"]}
        names = {name for name in names if pd.notna(name)}

        roles = create_list_from_input(row["Role List"], separator=",")

        keyword_names = get_list_nodes_from_string_via_list_name(
            string_with_list_labels=row["Keyword"], label_separator=",", list_name="Keyword", list_lookup=list_lookup
        )
        keyword_names = sorted(keyword_names)
        description_raw = row["Description"]
        footnote_text_raw = select_footnote_text(description_raw)
        footnote_text = (
            create_standoff_link_to_uri(uri=row["Footnote URI"], displayed_text=footnote_text_raw)
            if not pd.isna(row["Footnote URI"]) and is_nonempty_value(footnote_text_raw)
            else footnote_text_raw
        )
        if footnote_text:
            footnote = create_footnote_string(footnote_text=footnote_text)
            description = description_raw.replace(f"*{footnote_text_raw}*", footnote)
        else:
            description = description_raw
        authors_resource = create_list_from_input(input_value=row["Authorship Resource"], separator=",")

        # create resource, label and id
        resource = Resource.create_new(res_id=row["ID"], restype=":Character", label=row["Name EN"])

        # add properties to resource
        resource.add_simpletext("project-metadata:hasID", row["ID"])
        resource.add_simpletext_multiple(":hasName", names)
        resource.add_richtext(":hasDescription", description)

        resource.add_richtext_optional(prop_name=":hasDescriptionAlternative", value=row["Alternative Description"])
        resource.add_list_multiple(prop_name=":hasRoleList", list_name="Role", values=roles)
        resource.add_richtext_optional(":hasQuote", row["Quote"])
        resource.add_list_multiple(prop_name=":hasKeywordList", list_name="Keyword", values=keyword_names)
        resource.add_uri_optional(":hasWikidataLink", row["Wikidata Link"])
        resource.add_simpletext("project-metadata:hasCopyrightResource", "DaSCH")
        resource.add_list("project-metadata:hasLicenseResource", "License", "LIC_002")
        resource.add_simpletext_multiple("project-metadata:hasAuthorshipResource", authors_resource)

        # append resource to list
        all_resources.append(resource)

    return all_resources


if __name__ == "__main__":
    main()
