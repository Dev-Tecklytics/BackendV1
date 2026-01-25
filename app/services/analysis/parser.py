# from lxml import etree
# from collections import Counter
# import logging
# import json

# from app.domain.analysis_contracts import ParsedWorkflow

# logger = logging.getLogger(__name__)


# def parse_workflow(file_path: str, platform: str) -> ParsedWorkflow:
#     # Use XMLParser with recover mode to handle malformed XML
#     parser = etree.XMLParser(recover=True, remove_blank_text=True)
    
#     try:
#         tree = etree.parse(file_path, parser)
#         root = tree.getroot()
        
#         # Log any parser errors but continue
#         if parser.error_log:
#             logger.warning(f"XML parser warnings for {file_path}: {parser.error_log}")
#     except Exception as e:
#         logger.error(f"Failed to parse {file_path}: {str(e)}")
#         raise

#     # Platform-specific parsing
#     if platform == "UiPath":
#         activities = [el.tag for el in root.findall(".//*")]
#         variables = [el.get("Name") for el in root.findall(".//*[@Name]") if el.get("Name")]
#     elif platform == "Blue Prism":
#         # Blue Prism uses different structure
#         activities = [el.get("name") or el.tag for el in root.findall(".//stage") + root.findall(".//action")]
#         variables = [el.get("name") for el in root.findall(".//variable") if el.get("name")]
#     else:
#         # Generic XML parsing
#         activities = [el.tag for el in root.findall(".//*")]
#         variables = [el.get("Name") or el.get("name") for el in root.findall(".//*[@Name]") + root.findall(".//*[@name]") if el.get("Name") or el.get("name")]

#     nesting_depth = max(
#         (len(el.xpath("ancestor::*")) for el in root.findall(".//*")),
#         default=0
#     )

#     logger.info(f"Parsed {platform} workflow: {len(activities)} activities, {len(variables)} variables, depth {nesting_depth}")

#     return ParsedWorkflow(
#         platform=platform,
#         activities=activities,
#         variables=variables,
#         nesting_depth=nesting_depth,
#         raw_tree=root,
#     )

from lxml import etree
import logging
from app.domain.analysis_contracts import ParsedWorkflow

logger = logging.getLogger(__name__)


def parse_workflow(file_path: str, platform: str) -> ParsedWorkflow:
    parser = etree.XMLParser(recover=True, remove_blank_text=True)

    try:
        tree = etree.parse(file_path, parser)
        root = tree.getroot()

        if parser.error_log:
            logger.warning(f"XML parser warnings for {file_path}: {parser.error_log}")

    except Exception as e:
        logger.error(f"Failed to parse {file_path}: {str(e)}")
        raise

    # -----------------------------------
    # UiPath Parsing (FIXED PROPERLY)
    # -----------------------------------
    if platform == "UiPath":

        def clean_tag(tag):
            tag_str = str(tag) if tag is not None else ""
            return tag_str.split('}')[-1] if '}' in tag_str else tag_str

        # Infrastructure / Metadata elements to ignore
        IGNORED_TAGS = {
            "AssemblyReference",
            "TextExpression.NamespacesForImplementation",
            "TextExpression.ReferencesForImplementation",
            "WorkflowViewStateService.ViewState",
            "VisualBasic.Settings",
            "String",
            "Boolean",
            "Dictionary",
            "Collection",
            "sap2010:WorkflowViewState.IdRef",
        }

        activities = []
        variables = []

        for el in root.iter():
            tag_name = clean_tag(el.tag)

            # Skip root and infrastructure tags
            if tag_name in IGNORED_TAGS:
                continue

            # Skip pure namespace / metadata nodes
            if (
                tag_name.startswith("TextExpression")
                or tag_name.endswith("Reference")
                or tag_name.endswith("ViewState")
            ):
                continue

            # Capture variables
            if el.get("Name"):
                variables.append(el.get("Name"))

            # Skip non-activity container nodes
            if tag_name in {"Sequence", "Flowchart"}:
                continue

            # Add as activity
            activities.append(tag_name)

        real_nodes = [
            el for el in root.iter()
            if clean_tag(el.tag) not in IGNORED_TAGS
        ]

        raw_activities = []
        for el in real_nodes:
            tag = clean_tag(el.tag)
            if tag in {"Sequence", "Flowchart"}: continue
            raw_activities.append({
                "type": tag,
                "displayName": el.get("DisplayName") or tag
            })

        raw_variables = []
        for el in root.findall(".//*[@Name]"):
            v_name = el.get("Name")
            if v_name:
                raw_variables.append({
                    "name": v_name,
                    "defaultValue": el.get("Default") or ""
                })

        nesting_depth = max(
            (len([a for a in el.iterancestors()]) for el in real_nodes),
            default=0
        )

    # -----------------------------------
    # Blue Prism Parsing
    # -----------------------------------
    elif platform == "Blue Prism":

        activities_data = root.findall(".//stage") + root.findall(".//action")
        activities = [
            el.get("name") or el.tag
            for el in activities_data
        ]

        raw_activities = []
        for el in activities_data:
            raw_activities.append({
                "type": el.tag,
                "displayName": el.get("name") or el.tag
            })

        variables_data = root.findall(".//variable")
        variables = [
            el.get("name")
            for el in variables_data
            if el.get("name")
        ]

        raw_variables = []
        for el in variables_data:
            raw_variables.append({
                "name": el.get("name"),
                "type": el.get("type")
            })

        nesting_depth = max(
            (len(el.xpath("ancestor::*")) for el in root.findall(".//*")),
            default=0
        )

    # -----------------------------------
    # Generic XML Fallback
    # -----------------------------------
    else:
        activities = [el.tag for el in root.findall(".//*")]

        variables = [
            el.get("Name") or el.get("name")
            for el in root.findall(".//*[@Name]") + root.findall(".//*[@name]")
            if el.get("Name") or el.get("name")
        ]

        nesting_depth = max(
            (len(el.xpath("ancestor::*")) for el in root.findall(".//*")),
            default=0
        )

    logger.info(
        f"Parsed {platform} workflow: "
        f"{len(activities)} activities, "
        f"{len(variables)} variables, "
        f"depth {nesting_depth}"
    )

    return ParsedWorkflow(
        platform=platform,
        activities=activities,
        variables=variables,
        nesting_depth=nesting_depth,
        raw_activities=raw_activities if 'raw_activities' in locals() else [],
        raw_variables=raw_variables if 'raw_variables' in locals() else [],
        raw_tree=root,
    )
