GLOBAL_ATTRIBUTES = {
    "required": (
        "Data_type", "Data_version ", "Descriptor", "Discipline", "Instrument_type", "Logical_file_id",
        "Logical_source",
        "Logical_source_description", "Mission_group", "PI_affiliation", "PI_name", "Project", "Source_name", "TEXT"),
    "recommended": (
        "Acknowledgement", "DOI", "Generated_by", "Generation_date", "HTTP_LINK", "LINK_TEXT", "LINK_TITLE", "MODS",
        "Rules_of_use", "spase_DatasetResourceID", "Time_resolution"),
    "optional": ("Parents", "Skeleton_version", "Software_version", "TITLE", "Validate")
}

DATA_VAR_ATTRIBUTES = {
    "required":("CATDESC", "DEPEND_0", "DISPLAY_TYPE", "FIELDNAM", "FILLVAL"),
    "recommended": (),
    "optional": ()
}