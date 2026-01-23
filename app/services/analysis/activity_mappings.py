from typing import List, Dict, Optional, Any
import math

class ActivityMappingData:
    def __init__(self, uiPathActivity: str, bluePrismEquivalent: str, mappingType: str, effortEstimate: float, isDeprecated: bool, category: str, conversionNotes: str = ""):
        self.uiPathActivity = uiPathActivity
        self.bluePrismEquivalent = bluePrismEquivalent
        self.mappingType = mappingType # 'direct' | 'partial' | 'complex' | 'incompatible'
        self.conversionNotes = conversionNotes
        self.effortEstimate = effortEstimate
        self.isDeprecated = isDeprecated
        self.category = category

ACTIVITY_MAPPINGS = [
    # UI Automation Activities
    {"uiPathActivity": "Click", "bluePrismEquivalent": "Navigate (Click)", "mappingType": "direct", "effortEstimate": 0.5, "isDeprecated": False, "category": "UI", "conversionNotes": "Map selector to Application Modeller element"},
    {"uiPathActivity": "Type Into", "bluePrismEquivalent": "Write", "mappingType": "direct", "effortEstimate": 0.5, "isDeprecated": False, "category": "UI", "conversionNotes": "Map selector to Application Modeller element, convert text input"},
    {"uiPathActivity": "Get Text", "bluePrismEquivalent": "Read", "mappingType": "direct", "effortEstimate": 0.5, "isDeprecated": False, "category": "UI", "conversionNotes": "Map selector to Application Modeller element, store in data item"},
    {"uiPathActivity": "Select Item", "bluePrismEquivalent": "Select Item", "mappingType": "direct", "effortEstimate": 0.5, "isDeprecated": False, "category": "UI", "conversionNotes": "Map dropdown selector and item value"},
    {"uiPathActivity": "Element Exists", "bluePrismEquivalent": "Check Exists", "mappingType": "direct", "effortEstimate": 0.5, "isDeprecated": False, "category": "UI", "conversionNotes": "Use Wait stage with existence check"},
    {"uiPathActivity": "Find Element", "bluePrismEquivalent": "Identify", "mappingType": "partial", "effortEstimate": 1.0, "isDeprecated": False, "category": "UI", "conversionNotes": "May need Application Modeller adjustments for dynamic elements"},
    {"uiPathActivity": "Hover", "bluePrismEquivalent": "Global Mouse Click Centre", "mappingType": "partial", "effortEstimate": 1.0, "isDeprecated": False, "category": "UI", "conversionNotes": "Use Global Mouse position over element without click"},
    {"uiPathActivity": "Get Attribute", "bluePrismEquivalent": "Get Attribute", "mappingType": "direct", "effortEstimate": 0.5, "isDeprecated": False, "category": "UI", "conversionNotes": "Map element and attribute name"},
    
    # Data Manipulation Activities
    {"uiPathActivity": "Assign", "bluePrismEquivalent": "Calculation (Assignment)", "mappingType": "direct", "effortEstimate": 0.25, "isDeprecated": False, "category": "Data", "conversionNotes": "Convert to Calculation stage with assignment expression"},
    {"uiPathActivity": "Add Data Row", "bluePrismEquivalent": "Collections - Add Row", "mappingType": "direct", "effortEstimate": 0.5, "isDeprecated": False, "category": "Data", "conversionNotes": "Use Collections action to add row to collection"},
    {"uiPathActivity": "Build Data Table", "bluePrismEquivalent": "Create Collection", "mappingType": "partial", "effortEstimate": 1.5, "isDeprecated": False, "category": "Data", "conversionNotes": "Define collection structure, may require manual column mapping"},
    {"uiPathActivity": "For Each Row", "bluePrismEquivalent": "Loop Collection", "mappingType": "direct", "effortEstimate": 0.5, "isDeprecated": False, "category": "Data", "conversionNotes": "Use Loop stage with collection iteration"},
    {"uiPathActivity": "Filter Data Table", "bluePrismEquivalent": "Filter Collection", "mappingType": "direct", "effortEstimate": 1.0, "isDeprecated": False, "category": "Data", "conversionNotes": "Use Collection Manipulation action with filter criteria"},
    {"uiPathActivity": "Join Data Tables", "bluePrismEquivalent": "Merge Collections", "mappingType": "partial", "effortEstimate": 2.0, "isDeprecated": False, "category": "Data", "conversionNotes": "May require custom logic for complex join operations"},
    {"uiPathActivity": "Sort Data Table", "bluePrismEquivalent": "Sort Collection", "mappingType": "direct", "effortEstimate": 0.5, "isDeprecated": False, "category": "Data", "conversionNotes": "Use Collection Manipulation action with sort criteria"},
    
    # Control Flow Activities
    {"uiPathActivity": "If", "bluePrismEquivalent": "Decision", "mappingType": "direct", "effortEstimate": 0.5, "isDeprecated": False, "category": "Control", "conversionNotes": "Convert condition to Blue Prism expression syntax"},
    {"uiPathActivity": "While", "bluePrismEquivalent": "Loop (While)", "mappingType": "direct", "effortEstimate": 0.5, "isDeprecated": False, "category": "Control", "conversionNotes": "Convert loop condition to Blue Prism expression"},
    {"uiPathActivity": "Do While", "bluePrismEquivalent": "Loop (Do-While)", "mappingType": "partial", "effortEstimate": 1.0, "isDeprecated": False, "category": "Control", "conversionNotes": "May need restructuring as BP has different loop semantics"},
    {"uiPathActivity": "Switch", "bluePrismEquivalent": "Multi Calc", "mappingType": "partial", "effortEstimate": 1.5, "isDeprecated": False, "category": "Control", "conversionNotes": "Use Multi Calculation stage with multiple decision paths"},
    {"uiPathActivity": "Flow Decision", "bluePrismEquivalent": "Decision", "mappingType": "direct", "effortEstimate": 0.5, "isDeprecated": False, "category": "Control", "conversionNotes": "Convert to Decision stage in process flow"},
    {"uiPathActivity": "Flow Switch", "bluePrismEquivalent": "Multi Calc", "mappingType": "partial", "effortEstimate": 1.5, "isDeprecated": False, "category": "Control", "conversionNotes": "Map to multiple decision branches"},
    {"uiPathActivity": "Delay", "bluePrismEquivalent": "Wait", "mappingType": "direct", "effortEstimate": 0.25, "isDeprecated": False, "category": "Control", "conversionNotes": "Convert delay duration to Wait stage timeout"},
    
    # Error Handling Activities
    {"uiPathActivity": "Try Catch", "bluePrismEquivalent": "Exception Block", "mappingType": "direct", "effortEstimate": 1.0, "isDeprecated": False, "category": "Error", "conversionNotes": "Map to Exception stage with Recover/Resume paths"},
    {"uiPathActivity": "Throw", "bluePrismEquivalent": "Exception (Throw)", "mappingType": "direct", "effortEstimate": 0.5, "isDeprecated": False, "category": "Error", "conversionNotes": "Convert exception message and type"},
    {"uiPathActivity": "Rethrow", "bluePrismEquivalent": "Exception (Resume)", "mappingType": "partial", "effortEstimate": 0.5, "isDeprecated": False, "category": "Error", "conversionNotes": "Use Resume to propagate exception"},
    {"uiPathActivity": "Retry Scope", "bluePrismEquivalent": "Loop with Exception", "mappingType": "complex", "effortEstimate": 2.0, "isDeprecated": False, "category": "Error", "conversionNotes": "Requires custom loop logic with exception handling and retry counter"},
    
    # File Operations Activities
    {"uiPathActivity": "Read Text File", "bluePrismEquivalent": "File Management - Read Text", "mappingType": "direct", "effortEstimate": 0.5, "isDeprecated": False, "category": "File", "conversionNotes": "Map file path and encoding"},
    {"uiPathActivity": "Write Text File", "bluePrismEquivalent": "File Management - Write Text", "mappingType": "direct", "effortEstimate": 0.5, "isDeprecated": False, "category": "File", "conversionNotes": "Map file path, content, and encoding"},
    {"uiPathActivity": "Append Line", "bluePrismEquivalent": "File Management - Append Text", "mappingType": "direct", "effortEstimate": 0.5, "isDeprecated": False, "category": "File", "conversionNotes": "Map file path and content to append"},
    {"uiPathActivity": "Copy File", "bluePrismEquivalent": "File Management - Copy", "mappingType": "direct", "effortEstimate": 0.25, "isDeprecated": False, "category": "File", "conversionNotes": "Map source and destination paths"},
    {"uiPathActivity": "Move File", "bluePrismEquivalent": "File Management - Move", "mappingType": "direct", "effortEstimate": 0.25, "isDeprecated": False, "category": "File", "conversionNotes": "Map source and destination paths"},
    {"uiPathActivity": "Delete File", "bluePrismEquivalent": "File Management - Delete", "mappingType": "direct", "effortEstimate": 0.25, "isDeprecated": False, "category": "File", "conversionNotes": "Map file path"},
    {"uiPathActivity": "Path Exists", "bluePrismEquivalent": "File Management - Exists", "mappingType": "direct", "effortEstimate": 0.25, "isDeprecated": False, "category": "File", "conversionNotes": "Check file or folder existence"},
    
    # Excel Activities
    {"uiPathActivity": "Excel Application Scope", "bluePrismEquivalent": "MS Excel VBO - Create Instance", "mappingType": "partial", "effortEstimate": 1.0, "isDeprecated": False, "category": "Excel", "conversionNotes": "Use Excel VBO to create instance and open workbook"},
    {"uiPathActivity": "Read Range", "bluePrismEquivalent": "MS Excel VBO - Get Worksheet", "mappingType": "direct", "effortEstimate": 0.5, "isDeprecated": False, "category": "Excel", "conversionNotes": "Read data into collection"},
    {"uiPathActivity": "Write Range", "bluePrismEquivalent": "MS Excel VBO - Write Collection", "mappingType": "direct", "effortEstimate": 0.5, "isDeprecated": False, "category": "Excel", "conversionNotes": "Write collection to worksheet"},
    {"uiPathActivity": "Append Range", "bluePrismEquivalent": "MS Excel VBO - Append Row", "mappingType": "direct", "effortEstimate": 0.5, "isDeprecated": False, "category": "Excel", "conversionNotes": "Append data to end of worksheet"},
    
    # Email Activities
    {"uiPathActivity": "Send Outlook Mail Message", "bluePrismEquivalent": "MS Outlook VBO - Send Email", "mappingType": "direct", "effortEstimate": 0.5, "isDeprecated": False, "category": "Email", "conversionNotes": "Map email properties (to, subject, body, attachments)"},
    {"uiPathActivity": "Get Outlook Mail Messages", "bluePrismEquivalent": "MS Outlook VBO - Get Emails", "mappingType": "direct", "effortEstimate": 1.0, "isDeprecated": False, "category": "Email", "conversionNotes": "Map folder and filter criteria"},
    {"uiPathActivity": "Save Attachments", "bluePrismEquivalent": "MS Outlook VBO - Save Attachments", "mappingType": "direct", "effortEstimate": 0.5, "isDeprecated": False, "category": "Email", "conversionNotes": "Map save path and filter"},
    
    # Web Activities
    {"uiPathActivity": "Open Browser", "bluePrismEquivalent": "Browser Automation - Attach", "mappingType": "partial", "effortEstimate": 1.0, "isDeprecated": False, "category": "Web", "conversionNotes": "Configure browser type and URL in Application Modeller"},
    {"uiPathActivity": "Navigate To", "bluePrismEquivalent": "Browser Automation - Navigate", "mappingType": "direct", "effortEstimate": 0.25, "isDeprecated": False, "category": "Web", "conversionNotes": "Map URL navigation"},
    {"uiPathActivity": "Close Tab", "bluePrismEquivalent": "Browser Automation - Close Tab", "mappingType": "direct", "effortEstimate": 0.25, "isDeprecated": False, "category": "Web", "conversionNotes": "Close current browser tab"},
    
    # API/HTTP Activities
    {"uiPathActivity": "HTTP Request", "bluePrismEquivalent": "Web Services - REST", "mappingType": "direct", "effortEstimate": 1.0, "isDeprecated": False, "category": "API", "conversionNotes": "Map endpoint, method, headers, and body"},
    {"uiPathActivity": "Invoke Web Service", "bluePrismEquivalent": "Web Services - SOAP", "mappingType": "direct", "effortEstimate": 1.5, "isDeprecated": False, "category": "API", "conversionNotes": "Map WSDL and service parameters"},
    
    # Orchestrator/Queue Activities
    {"uiPathActivity": "Add Queue Item", "bluePrismEquivalent": "Work Queue - Add to Queue", "mappingType": "direct", "effortEstimate": 0.5, "isDeprecated": False, "category": "Queue", "conversionNotes": "Map queue name and item data"},
    {"uiPathActivity": "Get Transaction Item", "bluePrismEquivalent": "Work Queue - Get Next Item", "mappingType": "direct", "effortEstimate": 0.5, "isDeprecated": False, "category": "Queue", "conversionNotes": "Map queue name and lock item"},
    {"uiPathActivity": "Set Transaction Status", "bluePrismEquivalent": "Work Queue - Mark Complete/Exception", "mappingType": "direct", "effortEstimate": 0.5, "isDeprecated": False, "category": "Queue", "conversionNotes": "Map status (Completed/Failed) and exception details"},
    
    # Database Activities
    {"uiPathActivity": "Execute Query", "bluePrismEquivalent": "OLEDB - Execute", "mappingType": "direct", "effortEstimate": 0.5, "isDeprecated": False, "category": "Database", "conversionNotes": "Map connection string and SQL query"},
    {"uiPathActivity": "Execute Non Query", "bluePrismEquivalent": "OLEDB - Execute Non Query", "mappingType": "direct", "effortEstimate": 0.5, "isDeprecated": False, "category": "Database", "conversionNotes": "Map connection string and SQL statement"},
    
    # Logging Activities
    {"uiPathActivity": "Log Message", "bluePrismEquivalent": "Write to Log", "mappingType": "direct", "effortEstimate": 0.25, "isDeprecated": False, "category": "Logging", "conversionNotes": "Map log level and message"},
    
    # Credential Activities
    {"uiPathActivity": "Get Credential", "bluePrismEquivalent": "Credential Manager - Get", "mappingType": "direct", "effortEstimate": 0.5, "isDeprecated": False, "category": "Security", "conversionNotes": "Map credential name"},
    
    # Incompatible/Complex Activities
    {"uiPathActivity": "Invoke Code", "bluePrismEquivalent": "Code Stage", "mappingType": "complex", "effortEstimate": 3.0, "isDeprecated": False, "category": "Advanced", "conversionNotes": "Requires manual conversion of VB.NET/C# code to Blue Prism C# code stage syntax"},
    {"uiPathActivity": "Invoke Workflow File", "bluePrismEquivalent": "Sub-Process", "mappingType": "partial", "effortEstimate": 1.0, "isDeprecated": False, "category": "Workflow", "conversionNotes": "Map to Process or Object call with parameter mapping"},
    {"uiPathActivity": "Invoke Method", "bluePrismEquivalent": "Code Stage", "mappingType": "complex", "effortEstimate": 2.0, "isDeprecated": False, "category": "Advanced", "conversionNotes": "Requires implementation in C# code stage"},
    {"uiPathActivity": "Python Script", "bluePrismEquivalent": "N/A", "mappingType": "incompatible", "effortEstimate": 5.0, "isDeprecated": False, "category": "Advanced", "conversionNotes": "Blue Prism does not natively support Python. Consider external API call or reimplementation in C#"},
    {"uiPathActivity": "Computer Vision", "bluePrismEquivalent": "Surface Automation", "mappingType": "partial", "effortEstimate": 4.0, "isDeprecated": False, "category": "UI", "conversionNotes": "Use Blue Prism Surface Automation or Region mode, may require redesign"}
]

def get_uipath_to_blueprism_mapping(activity_name: str) -> Optional[Dict[str, Any]]:
    # Handle cases like "Click [UI Automation]" or namespace-qualified names
    clean_name = activity_name.split('{')[-1].split('}')[-1] # Simple cleanup
    for m in ACTIVITY_MAPPINGS:
        if m["uiPathActivity"].lower() == clean_name.lower():
            return m
    return None

def categorize_activity(activity_name: str) -> str:
    mapping = get_uipath_to_blueprism_mapping(activity_name)
    if mapping:
        return mapping["category"]
    
    # Fallback categorization if not in mapping
    control_flow = {"If", "ForEach", "While", "Switch", "FlowDecision", "FlowSwitch", "TryCatch", "RetryScope"}
    data_manipulation = {"Assign", "WriteLine", "ReadRange", "WriteRange", "AppendLine", "BuildDataTable", "AddDataRow"}
    workflow_invocation = {"InvokeWorkflowFile", "InvokeWorkflow"}

    if activity_name in control_flow:
        return "Control"
    elif activity_name in data_manipulation or "Data" in activity_name:
        return "Data"
    elif activity_name in workflow_invocation:
        return "Workflow"
    elif "Click" in activity_name or "Type" in activity_name or "Web" in activity_name:
        return "UI"
    
    return "Other"

def get_blueprism_to_uipath_mapping(bp_action: str) -> List[Dict[str, Any]]:
    return [m for m in ACTIVITY_MAPPINGS if m["bluePrismEquivalent"].lower() == bp_action.lower()]

def get_mappings_for_activities(activities: List[str], direction: str = 'UiPath-to-BP') -> List[Dict[str, Any]]:
    results = []
    for activity in activities:
        if direction == 'UiPath-to-BP':
            mappings = [get_uipath_to_blueprism_mapping(activity)]
            mappings = [m for m in mappings if m is not None]
        else:
            mappings = get_blueprism_to_uipath_mapping(activity)

        has_direct = any(m["mappingType"] == 'direct' for m in mappings)
        has_partial = any(m["mappingType"] == 'partial' for m in mappings)
        is_complex = any(m["mappingType"] == 'complex' for m in mappings)
        is_incompatible = len(mappings) == 0 or all(m["mappingType"] == 'incompatible' for m in mappings)

        results.append({
            "sourceActivity": activity,
            "mappings": mappings,
            "hasDirect": has_direct,
            "hasPartial": has_partial,
            "isComplex": is_complex,
            "isIncompatible": is_incompatible
        })
    return results

def calculate_migration_stats(activities: List[str], direction: str = 'UiPath-to-BP') -> Dict[str, Any]:
    mapping_results = get_mappings_for_activities(activities, direction)

    stats = {
        "totalActivities": len(activities),
        "directMappings": 0,
        "partialMappings": 0,
        "complexMappings": 0,
        "incompatibleMappings": 0,
        "totalEffortHours": 0.0,
        "compatibilityScore": 0
    }

    for result in mapping_results:
        if result["hasDirect"]:
            stats["directMappings"] += 1
            stats["totalEffortHours"] += result["mappings"][0]["effortEstimate"] if result["mappings"] else 0
        elif result["hasPartial"]:
            stats["partialMappings"] += 1
            stats["totalEffortHours"] += result["mappings"][0]["effortEstimate"] if result["mappings"] else 0
        elif result["isComplex"]:
            stats["complexMappings"] += 1
            stats["totalEffortHours"] += result["mappings"][0]["effortEstimate"] if result["mappings"] else 0
        elif result["isIncompatible"]:
            stats["incompatibleMappings"] += 1
            # Default 8 hours for custom implementation if incompatible or no mapping found
            stats["totalEffortHours"] += 8.0

    # Calculate compatibility score (weighted)
    if stats["totalActivities"] > 0:
        score = (
            (stats["directMappings"] * 100) +
            (stats["partialMappings"] * 70) +
            (stats["complexMappings"] * 40) +
            (stats["incompatibleMappings"] * 0)
        ) / stats["totalActivities"]
        stats["compatibilityScore"] = round(score)

    return stats
