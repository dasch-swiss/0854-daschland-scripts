import pandas as pd
from dsp_tools.xmllib import ListLookup, Resource, convert_to_bool_string, create_list_from_input, is_nonempty_value

from src.folder_paths import OUTPUT_FOLDER, PROCESSED_FOLDER


def main() -> list[Resource]:
    all_resources: list[Resource] = []

    # define json file path
    path_to_json = OUTPUT_FOLDER / "daschland.json"

    # define dataframe
    event_df = pd.read_csv(PROCESSED_FOLDER / "Event.csv", dtype="str")

    # create mapping for lists
    list_lookup = ListLookup.create_new(
        project_json_path=path_to_json,
        language_of_label="en",
        default_ontology="daschland",
    )

    # iterate through rows of dataframe:
    for _, row in event_df.iterrows():
        # define variables
        resource_id = row["ID"]
        resource_label = row["Name"]

        image_ids = create_list_from_input(row["Image ID"], separator=",")
        event_type = list_lookup.get_node_via_list_name(list_name="Event Type", node_label=row["Event Type List"])
        guest_ids = create_list_from_input(row["Guest ID"], separator=",")
        protagonist_ids = create_list_from_input(row["Protagonist ID"], separator=",")
        adventure_character_ids = create_list_from_input(row["Adventure Character ID"], separator=",")
        antagonist_ids = create_list_from_input(row["Antagonist ID"], separator=",")
        authors_resource = create_list_from_input(input_value=row["Authorship Resource"], separator=",")
        dangerous = convert_to_bool_string(row["Dangerous"]) if is_nonempty_value(row["Dangerous"]) else ""

        event_type_to_restype_lookup = {
            "Social": ":EventSocial",
            "Conflict": ":EventConflict",
            "Adventure": ":EventAdventure",
            "Alternative": ":EventAlternative",
        }

        class_name = event_type_to_restype_lookup.get(row["Event Type"])
        if class_name is not None:
            resource = Resource.create_new(
                res_id=resource_id,
                restype=class_name,
                label=resource_label,
                authorship=authors_resource,
            )
        else:
            continue  # TODO: check if this is desired

        # add properties to resource
        resource.add_simpletext("project-metadata:hasID", resource_id)
        resource.add_simpletext(":hasName", row["Name"])
        resource.add_richtext(":hasDescription", row["Description"])
        resource.add_link_multiple(":linkToImage", image_ids)
        resource.add_list_optional(":hasEventTypeList", "Event Type", event_type)

        # add properties for social event:
        resource.add_link_multiple(":linkToCharacter", guest_ids)
        resource.add_integer_optional(":hasGuestAmount", row["Guest Amount"])

        # add properties for conflict event:
        resource.add_link_multiple(":linkToCharacterProtagonist", protagonist_ids)
        resource.add_link_multiple(":linkToCharacterAntagonist", antagonist_ids)

        # add properties for adventure event:
        resource.add_link_multiple(":linkToCharacter", adventure_character_ids)
        resource.add_bool_optional(":isDangerous", dangerous)

        # add resource to list
        all_resources.append(resource)

    return all_resources


if __name__ == "__main__":
    main()
