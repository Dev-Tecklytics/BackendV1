from lxml import etree
from collections import Counter

from app.domain.analysis_contracts import ParsedWorkflow


def parse_workflow(file_path: str, platform: str) -> ParsedWorkflow:
    tree = etree.parse(file_path)
    root = tree.getroot()

    activities = [el.tag for el in root.findall(".//*")]
    variables = [el.get("Name") for el in root.findall(".//*[@Name]") if el.get("Name")]

    nesting_depth = max(
        (len(el.xpath("ancestor::*")) for el in root.findall(".//*")),
        default=0
    )

    return ParsedWorkflow(
        platform=platform,
        activities=activities,
        variables=variables,
        nesting_depth=nesting_depth,
        raw_tree=root,
    )
