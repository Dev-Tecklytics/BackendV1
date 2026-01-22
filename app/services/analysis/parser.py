from lxml import etree
from collections import Counter
import logging
import json

from app.domain.analysis_contracts import ParsedWorkflow

logger = logging.getLogger(__name__)


def parse_workflow(file_path: str, platform: str) -> ParsedWorkflow:
    # Use XMLParser with recover mode to handle malformed XML
    parser = etree.XMLParser(recover=True, remove_blank_text=True)
    
    try:
        tree = etree.parse(file_path, parser)
        root = tree.getroot()
        
        # Log any parser errors but continue
        if parser.error_log:
            logger.warning(f"XML parser warnings for {file_path}: {parser.error_log}")
    except Exception as e:
        logger.error(f"Failed to parse {file_path}: {str(e)}")
        raise

    # Platform-specific parsing
    if platform == "UiPath":
        activities = [el.tag for el in root.findall(".//*")]
        variables = [el.get("Name") for el in root.findall(".//*[@Name]") if el.get("Name")]
    elif platform == "Blue Prism":
        # Blue Prism uses different structure
        activities = [el.get("name") or el.tag for el in root.findall(".//stage") + root.findall(".//action")]
        variables = [el.get("name") for el in root.findall(".//variable") if el.get("name")]
    else:
        # Generic XML parsing
        activities = [el.tag for el in root.findall(".//*")]
        variables = [el.get("Name") or el.get("name") for el in root.findall(".//*[@Name]") + root.findall(".//*[@name]") if el.get("Name") or el.get("name")]

    nesting_depth = max(
        (len(el.xpath("ancestor::*")) for el in root.findall(".//*")),
        default=0
    )

    logger.info(f"Parsed {platform} workflow: {len(activities)} activities, {len(variables)} variables, depth {nesting_depth}")

    return ParsedWorkflow(
        platform=platform,
        activities=activities,
        variables=variables,
        nesting_depth=nesting_depth,
        raw_tree=root,
    )
