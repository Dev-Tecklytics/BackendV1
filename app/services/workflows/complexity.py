from lxml import etree


def analyze_workflow(file_path: str) -> dict:
    tree = etree.parse(file_path)
    root = tree.getroot()

    activities = root.findall(".//*")
    variables = root.findall(".//*[@Name]")
    depth = max(len(el.xpath("ancestor::*")) for el in activities)

    score = (
        len(activities) * 1
        + depth * 3
        + len(variables) * 1
    )

    if score < 20:
        level = "Low"
    elif score < 50:
        level = "Medium"
    elif score < 100:
        level = "High"
    else:
        level = "Very High"

    return {
        "activity_count": len(activities),
        "variable_count": len(variables),
        "nesting_depth": depth,
        "complexity_score": score,
        "complexity_level": level,
    }
