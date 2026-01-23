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
            return tag.split('}')[-1] if '}' in tag else tag

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

        # Calculate nesting depth only for real activity nodes
        real_nodes = [
            el for el in root.iter()
            if clean_tag(el.tag) not in IGNORED_TAGS
        ]

        nesting_depth = max(
            (len([a for a in el.iterancestors()]) for el in real_nodes),
            default=0
        )

    # -----------------------------------
    # Blue Prism Parsing
    # -----------------------------------
    elif platform == "Blue Prism":

        activities = [
            el.get("name") or el.tag
            for el in root.findall(".//stage") + root.findall(".//action")
        ]

        variables = [
            el.get("name")
            for el in root.findall(".//variable")
            if el.get("name")
        ]

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
        raw_tree=root,
    )
