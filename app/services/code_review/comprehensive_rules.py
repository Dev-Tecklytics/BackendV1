from typing import List, Dict, Any, Callable
from dataclasses import dataclass


@dataclass
class CodeReviewFinding:
    """Individual code review finding"""
    category: str
    severity: str
    rule_id: str
    rule_name: str
    message: str
    description: str
    recommendation: str
    activity_name: str = None
    location: str = None
    code_snippet: str = None
    impact: str = None
    effort: str = None


@dataclass
class CodeReviewRule:
    """Code review rule definition"""
    id: str
    name: str
    category: str  # Naming, ErrorHandling, Performance, Security, Maintainability, Standards
    severity: str  # Critical, Major, Minor, Info
    platform: str  # UiPath, BluePrism, Both
    description: str
    check_function: Callable[[Dict[str, Any], List[Dict[str, Any]]], List[CodeReviewFinding]]


# ============================================
# UIPATH RULES
# ============================================

def check_workflow_naming(workflow: Dict, activities: List[Dict]) -> List[CodeReviewFinding]:
    """UP-NAM-001: Workflow Naming Convention"""
    findings = []
    name = workflow.get('workflowName', '')
    
    # Check for PascalCase
    if name and not (name[0].isupper() and name.replace('_', '').isalnum()):
        findings.append(CodeReviewFinding(
            category='Naming',
            severity='Minor',
            rule_id='UP-NAM-001',
            rule_name='Workflow Naming Convention',
            message=f'Workflow name "{name}" does not follow PascalCase convention',
            description='Workflow names should use PascalCase (e.g., ProcessInvoice, ValidateData) for consistency and readability',
            recommendation='Rename workflow to use PascalCase. Example: "process_invoice" → "ProcessInvoice"',
            activity_name=name,
            impact='Maintainability',
            effort='Low'
        ))
    
    # Check for generic names
    generic_names = ['workflow', 'process', 'main', 'sequence', 'test']
    if any(gen in name.lower() for gen in generic_names) and len(name) < 15:
        findings.append(CodeReviewFinding(
            category='Naming',
            severity='Minor',
            rule_id='UP-NAM-001',
            rule_name='Workflow Naming Convention',
            message=f'Workflow name "{name}" is too generic',
            description='Workflow names should be descriptive and indicate the business purpose',
            recommendation='Use a more specific name that describes what the workflow does (e.g., ExtractInvoiceData, ValidateCustomerInfo)',
            activity_name=name,
            impact='Maintainability',
            effort='Low'
        ))
    
    return findings


def check_variable_naming(workflow: Dict, activities: List[Dict]) -> List[CodeReviewFinding]:
    """UP-NAM-002: Variable Naming Convention"""
    findings = []
    variables = workflow.get('variables', [])
    
    for variable in variables:
        var_name = variable.get('name', '')
        
        # Check for camelCase
        if var_name and not (var_name[0].islower() and var_name.replace('_', '').isalnum()):
            findings.append(CodeReviewFinding(
                category='Naming',
                severity='Minor',
                rule_id='UP-NAM-002',
                rule_name='Variable Naming Convention',
                message=f'Variable "{var_name}" does not follow camelCase convention',
                description='Variables should use camelCase (e.g., invoiceNumber, customerData) for consistency',
                recommendation='Rename variable to use camelCase. Example: "Invoice_Number" → "invoiceNumber"',
                activity_name=var_name,
                impact='Maintainability',
                effort='Low'
            ))
        
        # Check for too short names
        if len(var_name) == 1 or (len(var_name) == 2 and var_name.lower() not in ['dt', 'id']):
            findings.append(CodeReviewFinding(
                category='Naming',
                severity='Minor',
                rule_id='UP-NAM-002',
                rule_name='Variable Naming Convention',
                message=f'Variable "{var_name}" is too short and not descriptive',
                description='Variable names should be descriptive enough to understand their purpose',
                recommendation='Use a more descriptive name (e.g., "i" → "index", "x" → "customerName")',
                activity_name=var_name,
                impact='Maintainability',
                effort='Low'
            ))
    
    return findings


def check_missing_try_catch(workflow: Dict, activities: List[Dict]) -> List[CodeReviewFinding]:
    """UP-ERR-001: Missing Try-Catch Blocks"""
    findings = []
    
    has_try_catch = any(
        'trycatch' in act.get('type', '').lower() or 
        'try catch' in act.get('displayName', '').lower()
        for act in activities
    )
    
    activity_count = len(activities)
    
    if not has_try_catch and activity_count > 5:
        findings.append(CodeReviewFinding(
            category='ErrorHandling',
            severity='Critical',
            rule_id='UP-ERR-001',
            rule_name='Missing Try-Catch Blocks',
            message='Workflow lacks error handling mechanisms',
            description=f'This workflow has {activity_count} activities but no Try-Catch blocks for error handling',
            recommendation='Wrap critical operations in Try-Catch blocks. Add global error handler at workflow level and specific handlers for risky operations (API calls, file operations, database queries)',
            impact='Critical - Production failures without proper error handling',
            effort='Medium'
        ))
    
    return findings


def check_empty_catch_blocks(workflow: Dict, activities: List[Dict]) -> List[CodeReviewFinding]:
    """UP-ERR-002: Empty Catch Blocks"""
    findings = []
    
    try_catch_activities = [act for act in activities if 'trycatch' in act.get('type', '').lower()]
    
    if try_catch_activities:
        findings.append(CodeReviewFinding(
            category='ErrorHandling',
            severity='Info',
            rule_id='UP-ERR-002',
            rule_name='Empty Catch Blocks',
            message='Review catch blocks to ensure proper error logging',
            description='All catch blocks should log errors with sufficient detail for debugging',
            recommendation='Ensure each catch block logs: error message, timestamp, workflow name, and context data. Use Log Message activity or custom logging framework',
            impact='Maintainability - Difficult to debug production issues',
            effort='Low'
        ))
    
    return findings


def check_retry_logic(workflow: Dict, activities: List[Dict]) -> List[CodeReviewFinding]:
    """UP-ERR-003: No Retry Logic for Transient Failures"""
    findings = []
    
    has_http = any(
        'http' in act.get('type', '').lower() or
        'invoke' in act.get('type', '').lower() or
        'api' in act.get('displayName', '').lower() or
        'web service' in act.get('displayName', '').lower()
        for act in activities
    )
    
    has_retry = any(
        'retry' in act.get('type', '').lower() or
        'retry' in act.get('displayName', '').lower()
        for act in activities
    )
    
    if has_http and not has_retry:
        findings.append(CodeReviewFinding(
            category='ErrorHandling',
            severity='Major',
            rule_id='UP-ERR-003',
            rule_name='No Retry Logic for Transient Failures',
            message='API/HTTP activities detected without retry logic',
            description='Network operations can fail transiently and should have automatic retry mechanisms',
            recommendation='Wrap HTTP/API calls in Retry Scope activity with exponential backoff. Configure 3-5 retries with increasing intervals (1s, 2s, 4s)',
            impact='Reliability - Temporary network issues cause permanent failures',
            effort='Low'
        ))
    
    return findings


def check_excessive_nesting(workflow: Dict, activities: List[Dict]) -> List[CodeReviewFinding]:
    """UP-PERF-001: Excessive Nesting Depth"""
    findings = []
    nesting_depth = workflow.get('nestingDepth', 0)
    
    if nesting_depth > 5:
        findings.append(CodeReviewFinding(
            category='Performance',
            severity='Major',
            rule_id='UP-PERF-001',
            rule_name='Excessive Nesting Depth',
            message=f'Nesting depth of {nesting_depth} exceeds recommended maximum',
            description='Deep nesting makes workflows hard to read, maintain, and can impact performance',
            recommendation='Refactor deeply nested logic into separate workflows or use sub-workflows. Maximum recommended nesting: 5 levels',
            impact='Performance & Maintainability',
            effort='High'
        ))
    
    return findings


def check_large_workflow(workflow: Dict, activities: List[Dict]) -> List[CodeReviewFinding]:
    """UP-PERF-002: Large Workflow - Consider Modularization"""
    findings = []
    activity_count = len(activities)
    
    if activity_count > 50:
        severity = 'Major' if activity_count > 100 else 'Minor'
        findings.append(CodeReviewFinding(
            category='Performance',
            severity=severity,
            rule_id='UP-PERF-002',
            rule_name='Large Workflow - Consider Modularization',
            message=f'Workflow has {activity_count} activities, exceeding recommended size',
            description='Large workflows are difficult to maintain, test, and reuse. Best practice is to keep workflows under 50 activities',
            recommendation='Break down workflow into logical sub-workflows based on functional boundaries. Use Invoke Workflow File activity to call sub-workflows',
            impact='Maintainability & Performance',
            effort='High'
        ))
    
    return findings


def check_selector_optimization(workflow: Dict, activities: List[Dict]) -> List[CodeReviewFinding]:
    """UP-PERF-003: Selector Optimization"""
    findings = []
    
    ui_activities = [
        act for act in activities
        if any(keyword in act.get('type', '').lower() for keyword in ['click', 'type', 'get']) or
           any(keyword in act.get('displayName', '').lower() for keyword in ['click', 'type into'])
    ]
    
    if len(ui_activities) > 10:
        findings.append(CodeReviewFinding(
            category='Performance',
            severity='Info',
            rule_id='UP-PERF-003',
            rule_name='Selector Optimization',
            message=f'Workflow has {len(ui_activities)} UI activities - review selector performance',
            description='Multiple UI activities detected. Ensure selectors use stable attributes (idx should be avoided)',
            recommendation='Use UiPath UI Explorer to validate selectors. Prefer ID and Name attributes over positional indices. Consider using Anchors for dynamic UIs',
            impact='Performance - Slow selector resolution',
            effort='Medium'
        ))
    
    return findings


def check_hardcoded_credentials(workflow: Dict, activities: List[Dict]) -> List[CodeReviewFinding]:
    """UP-SEC-001: Hardcoded Credentials"""
    findings = []
    variables = workflow.get('variables', [])
    
    suspicious_patterns = ['password', 'pwd', 'pass', 'credential', 'secret', 'apikey', 'api_key', 'token']
    
    for variable in variables:
        var_name = variable.get('name', '').lower()
        var_value = variable.get('defaultValue', '')
        
        if any(pattern in var_name for pattern in suspicious_patterns):
            if var_value and len(var_value) > 0 and 'Config' not in var_value and 'Asset' not in var_value:
                findings.append(CodeReviewFinding(
                    category='Security',
                    severity='Critical',
                    rule_id='UP-SEC-001',
                    rule_name='Hardcoded Credentials',
                    message=f'Potential hardcoded credential found in variable "{variable.get("name")}"',
                    description='Credentials should never be stored in workflow code. Use Orchestrator Assets or Windows Credential Manager',
                    recommendation='Replace hardcoded value with Get Credential activity or Get Orchestrator Asset activity. Store credentials in Orchestrator vault',
                    activity_name=variable.get('name'),
                    impact='Security - Credential exposure risk',
                    effort='Low'
                ))
    
    return findings


def check_sensitive_data_logging(workflow: Dict, activities: List[Dict]) -> List[CodeReviewFinding]:
    """UP-SEC-002: Sensitive Data Logging"""
    findings = []
    
    log_activities = [
        act for act in activities
        if 'log' in act.get('type', '').lower() or 'log' in act.get('displayName', '').lower()
    ]
    
    if log_activities:
        findings.append(CodeReviewFinding(
            category='Security',
            severity='Info',
            rule_id='UP-SEC-002',
            rule_name='Sensitive Data Logging',
            message='Review log activities to ensure no sensitive data is logged',
            description='Log statements should not contain PII, credentials, or sensitive business data',
            recommendation='Review all Log Message activities. Mask or redact sensitive fields before logging. Use appropriate log levels (Info, Debug, Error)',
            impact='Security - Data exposure in logs',
            effort='Low'
        ))
    
    return findings


def check_missing_annotations(workflow: Dict, activities: List[Dict]) -> List[CodeReviewFinding]:
    """UP-MAINT-001: Missing Annotations"""
    findings = []
    activity_count = len(activities)
    
    if activity_count > 20:
        findings.append(CodeReviewFinding(
            category='Maintainability',
            severity='Minor',
            rule_id='UP-MAINT-001',
            rule_name='Missing Annotations',
            message='Complex workflow should have annotations for better understanding',
            description='Annotations help other developers understand workflow logic, especially for complex processes',
            recommendation='Add annotation activities to explain: business logic, decision points, data transformations, and integration points',
            impact='Maintainability - Difficult for others to understand',
            effort='Low'
        ))
    
    return findings


def check_logging_standards(workflow: Dict, activities: List[Dict]) -> List[CodeReviewFinding]:
    """UP-STD-001: Logging Standards"""
    findings = []
    
    has_logging = any(
        'log' in act.get('type', '').lower() or 'log' in act.get('displayName', '').lower()
        for act in activities
    )
    
    if not has_logging and len(activities) > 10:
        findings.append(CodeReviewFinding(
            category='Standards',
            severity='Minor',
            rule_id='UP-STD-001',
            rule_name='Logging Standards',
            message='Workflow lacks logging activities',
            description='Best practice is to log key events: workflow start, workflow end, errors, and major decision points',
            recommendation='Add Log Message activities at: workflow entry, workflow exit, error catch blocks, and before/after critical operations',
            impact='Maintainability - Difficult to troubleshoot issues',
            effort='Low'
        ))
    
    return findings


# Define all UiPath rules
UIPATH_RULES = [
    CodeReviewRule(
        id='UP-NAM-001',
        name='Workflow Naming Convention',
        category='Naming',
        severity='Minor',
        platform='UiPath',
        description='Workflow names should use PascalCase and be descriptive',
        check_function=check_workflow_naming
    ),
    CodeReviewRule(
        id='UP-NAM-002',
        name='Variable Naming Convention',
        category='Naming',
        severity='Minor',
        platform='UiPath',
        description='Variables should use camelCase with descriptive names',
        check_function=check_variable_naming
    ),
    CodeReviewRule(
        id='UP-ERR-001',
        name='Missing Try-Catch Blocks',
        category='ErrorHandling',
        severity='Critical',
        platform='UiPath',
        description='Workflows should have proper error handling with Try-Catch blocks',
        check_function=check_missing_try_catch
    ),
    CodeReviewRule(
        id='UP-ERR-002',
        name='Empty Catch Blocks',
        category='ErrorHandling',
        severity='Major',
        platform='UiPath',
        description='Catch blocks should not be empty and should log errors',
        check_function=check_empty_catch_blocks
    ),
    CodeReviewRule(
        id='UP-ERR-003',
        name='No Retry Logic for Transient Failures',
        category='ErrorHandling',
        severity='Major',
        platform='UiPath',
        description='API calls and network operations should have retry logic',
        check_function=check_retry_logic
    ),
    CodeReviewRule(
        id='UP-PERF-001',
        name='Excessive Nesting Depth',
        category='Performance',
        severity='Major',
        platform='UiPath',
        description='Deep nesting can impact performance and readability',
        check_function=check_excessive_nesting
    ),
    CodeReviewRule(
        id='UP-PERF-002',
        name='Large Workflow - Consider Modularization',
        category='Performance',
        severity='Minor',
        platform='UiPath',
        description='Large workflows should be split into smaller, reusable components',
        check_function=check_large_workflow
    ),
    CodeReviewRule(
        id='UP-PERF-003',
        name='Selector Optimization',
        category='Performance',
        severity='Minor',
        platform='UiPath',
        description='UI selectors should be optimized for performance',
        check_function=check_selector_optimization
    ),
    CodeReviewRule(
        id='UP-SEC-001',
        name='Hardcoded Credentials',
        category='Security',
        severity='Critical',
        platform='UiPath',
        description='Credentials should not be hardcoded in workflows',
        check_function=check_hardcoded_credentials
    ),
    CodeReviewRule(
        id='UP-SEC-002',
        name='Sensitive Data Logging',
        category='Security',
        severity='Major',
        platform='UiPath',
        description='Ensure sensitive data is not logged',
        check_function=check_sensitive_data_logging
    ),
    CodeReviewRule(
        id='UP-MAINT-001',
        name='Missing Annotations',
        category='Maintainability',
        severity='Minor',
        platform='UiPath',
        description='Complex workflows should have annotations explaining logic',
        check_function=check_missing_annotations
    ),
    CodeReviewRule(
        id='UP-STD-001',
        name='Logging Standards',
        category='Standards',
        severity='Minor',
        platform='UiPath',
        description='Workflows should follow logging best practices',
        check_function=check_logging_standards
    ),
]


# ============================================
# BLUE PRISM RULES
# ============================================

def check_bp_process_naming(workflow: Dict, activities: List[Dict]) -> List[CodeReviewFinding]:
    """BP-NAM-001: Process Naming Convention"""
    findings = []
    name = workflow.get('workflowName', '')
    
    if name and len(name) < 5:
        findings.append(CodeReviewFinding(
            category='Naming',
            severity='Minor',
            rule_id='BP-NAM-001',
            rule_name='Process Naming Convention',
            message=f'Process name "{name}" is too short',
            description='Process names should be descriptive and indicate business purpose',
            recommendation='Use a descriptive name like "Process - Invoice Validation" or "Utility - Data Extraction"',
            activity_name=name,
            impact='Maintainability',
            effort='Low'
        ))
    
    return findings


def check_bp_data_item_naming(workflow: Dict, activities: List[Dict]) -> List[CodeReviewFinding]:
    """BP-NAM-002: Data Item Naming"""
    findings = []
    variables = workflow.get('variables', [])
    
    generic_names = ['data', 'temp', 'var', 'x', 'y', 'z']
    
    for variable in variables:
        var_name = variable.get('name', '')
        
        if var_name.lower() in generic_names:
            findings.append(CodeReviewFinding(
                category='Naming',
                severity='Minor',
                rule_id='BP-NAM-002',
                rule_name='Data Item Naming',
                message=f'Data item "{var_name}" has a generic name',
                description='Data items should have descriptive names that indicate their purpose',
                recommendation='Use meaningful names like "Customer Name", "Invoice Total", or "Transaction ID"',
                activity_name=var_name,
                impact='Maintainability',
                effort='Low'
            ))
    
    return findings


def check_bp_missing_exception_handling(workflow: Dict, activities: List[Dict]) -> List[CodeReviewFinding]:
    """BP-ERR-001: Missing Exception Handling"""
    findings = []
    
    has_exception_handling = any(
        'exception' in act.get('type', '').lower() or
        'exception' in act.get('displayName', '').lower() or
        'error' in act.get('displayName', '').lower()
        for act in activities
    )
    
    if not has_exception_handling and len(activities) > 5:
        findings.append(CodeReviewFinding(
            category='ErrorHandling',
            severity='Critical',
            rule_id='BP-ERR-001',
            rule_name='Missing Exception Handling',
            message='Process lacks exception handling stages',
            description='All Blue Prism processes should have exception handling blocks for robustness',
            recommendation='Add Exception stages with Recover/Resume paths. Include error logging and notification mechanisms',
            impact='Critical - Unhandled exceptions cause process failures',
            effort='Medium'
        ))
    
    return findings


def check_bp_credential_management(workflow: Dict, activities: List[Dict]) -> List[CodeReviewFinding]:
    """BP-SEC-001: Credential Management"""
    findings = []
    variables = workflow.get('variables', [])
    
    suspicious_patterns = ['password', 'pwd', 'credential', 'secret', 'apikey']
    
    for variable in variables:
        var_name = variable.get('name', '').lower()
        
        if any(pattern in var_name for pattern in suspicious_patterns):
            findings.append(CodeReviewFinding(
                category='Security',
                severity='Critical',
                rule_id='BP-SEC-001',
                rule_name='Credential Management',
                message=f'Potential credential data item detected: "{variable.get("name")}"',
                description='Credentials should be stored in Blue Prism Credential Manager, not as plain data items',
                recommendation='Use Get Credential action from Credential Manager. Never store credentials as plain text data items',
                activity_name=variable.get('name'),
                impact='Security - Credential exposure',
                effort='Low'
            ))
    
    return findings


BLUEPRISM_RULES = [
    CodeReviewRule(
        id='BP-NAM-001',
        name='Process Naming Convention',
        category='Naming',
        severity='Minor',
        platform='BluePrism',
        description='Process names should follow Blue Prism naming standards',
        check_function=check_bp_process_naming
    ),
    CodeReviewRule(
        id='BP-NAM-002',
        name='Data Item Naming',
        category='Naming',
        severity='Minor',
        platform='BluePrism',
        description='Data items should use meaningful names',
        check_function=check_bp_data_item_naming
    ),
    CodeReviewRule(
        id='BP-ERR-001',
        name='Missing Exception Handling',
        category='ErrorHandling',
        severity='Critical',
        platform='BluePrism',
        description='Processes should have exception stages',
        check_function=check_bp_missing_exception_handling
    ),
    CodeReviewRule(
        id='BP-SEC-001',
        name='Credential Management',
        category='Security',
        severity='Critical',
        platform='BluePrism',
        description='Use Credential Manager for sensitive data',
        check_function=check_bp_credential_management
    ),
]


# ============================================
# REVIEW ENGINE
# ============================================

def perform_code_review(platform: str, workflow: Dict, activities: List[Dict]) -> Dict[str, Any]:
    """
    Execute comprehensive code review
    
    Returns:
        {
            'findings': List[CodeReviewFinding],
            'categoryScores': Dict[str, int],
            'overallScore': float,
            'qualityGrade': str
        }
    """
    # Select appropriate rules
    platform_rules = UIPATH_RULES if platform == 'UiPath' else BLUEPRISM_RULES
    
    # Execute all rules
    findings = []
    
    for rule in platform_rules:
        try:
            rule_findings = rule.check_function(workflow, activities)
            findings.extend(rule_findings)
        except Exception as e:
            print(f"Error executing rule {rule.id}: {e}")
    
    # Calculate category scores
    categories = ['Naming', 'ErrorHandling', 'Performance', 'Security', 'Maintainability', 'Standards']
    category_scores = {}
    
    for category in categories:
        category_findings = [f for f in findings if f.category == category]
        
        # Deduct points based on severity
        deductions = 0
        for finding in category_findings:
            if finding.severity == 'Critical':
                deductions += 25
            elif finding.severity == 'Major':
                deductions += 15
            elif finding.severity == 'Minor':
                deductions += 5
            elif finding.severity == 'Info':
                deductions += 2
        
        category_scores[category] = max(0, 100 - min(deductions, 100))
    
    # Calculate overall score (weighted average)
    weights = {
        'Naming': 0.1,
        'ErrorHandling': 0.3,
        'Performance': 0.2,
        'Security': 0.25,
        'Maintainability': 0.1,
        'Standards': 0.05
    }
    
    overall_score = sum(category_scores.get(cat, 0) * weight for cat, weight in weights.items())
    
    # Determine quality grade
    if overall_score >= 90:
        quality_grade = 'A'
    elif overall_score >= 80:
        quality_grade = 'B'
    elif overall_score >= 70:
        quality_grade = 'C'
    elif overall_score >= 60:
        quality_grade = 'D'
    else:
        quality_grade = 'F'
    
    return {
        'findings': findings,
        'categoryScores': category_scores,
        'overallScore': round(overall_score, 1),
        'qualityGrade': quality_grade
    }


def get_severity_counts(findings: List[CodeReviewFinding]) -> Dict[str, int]:
    """Get counts of findings by severity"""
    return {
        'critical': len([f for f in findings if f.severity == 'Critical']),
        'major': len([f for f in findings if f.severity == 'Major']),
        'minor': len([f for f in findings if f.severity == 'Minor']),
        'info': len([f for f in findings if f.severity == 'Info']),
        'total': len(findings)
    }
