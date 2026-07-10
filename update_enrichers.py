import os
import glob

enrichers_dir = "backend/app/enrichment/enrichers/static"

replacements = {
    "framework.py": [
        ("context.node.metadata.framework = (\"FastAPI\", 0.9)", "context.node.metadata.framework = (\"FastAPI\", 0.9)\n                        context.add_provenance('framework', 'FrameworkEnricher', 0.9, 'Found fastapi import')"),
        ("context.node.metadata.framework = (\"Express\", 0.9)", "context.node.metadata.framework = (\"Express\", 0.9)\n                        context.add_provenance('framework', 'FrameworkEnricher', 0.9, 'Found express import')"),
        ("context.node.metadata.framework = (\"Spring Boot\", 0.9)", "context.node.metadata.framework = (\"Spring Boot\", 0.9)\n                        context.add_provenance('framework', 'FrameworkEnricher', 0.9, 'Found spring import')"),
    ],
    "layer.py": [
        ("context.node.metadata.layer = (\"Controller\", 0.8)", "context.node.metadata.layer = (\"Controller\", 0.8)\n                context.add_provenance('layer', 'LayerEnricher', 0.8, 'Path matched controller/api/route')"),
        ("context.node.metadata.layer = (\"Service\", 0.8)", "context.node.metadata.layer = (\"Service\", 0.8)\n                context.add_provenance('layer', 'LayerEnricher', 0.8, 'Path matched service')"),
        ("context.node.metadata.layer = (\"Repository\", 0.8)", "context.node.metadata.layer = (\"Repository\", 0.8)\n                context.add_provenance('layer', 'LayerEnricher', 0.8, 'Path matched repo/model/db')"),
        ("context.node.metadata.layer = (\"Controller\", 0.9)", "context.node.metadata.layer = (\"Controller\", 0.9)\n                context.add_provenance('layer', 'LayerEnricher', 0.9, 'Name matched controller')"),
        ("context.node.metadata.layer = (\"Service\", 0.9)", "context.node.metadata.layer = (\"Service\", 0.9)\n                context.add_provenance('layer', 'LayerEnricher', 0.9, 'Name matched service')")
    ],
    "purpose.py": [
        ("context.node.semantics.purposes.extend(purposes)", "context.node.semantics.purposes.extend(purposes)\n            context.add_provenance('purposes', 'PurposeEnricher', purposes[0][1], 'Name/Path heuristics match')")
    ],
    "summary.py": [
        ("node.semantics.summary = (f\"Endpoint for {primary_purpose.lower()}.\", 0.6)", "node.semantics.summary = (f\"Endpoint for {primary_purpose.lower()}.\", 0.6)\n                context.add_provenance('summary', 'SummaryEnricher', 0.6, 'Endpoint format rule')"),
        ("node.semantics.summary = (f\"Component handling {primary_purpose.lower()}.\", 0.6)", "node.semantics.summary = (f\"Component handling {primary_purpose.lower()}.\", 0.6)\n                context.add_provenance('summary', 'SummaryEnricher', 0.6, 'Component format rule')"),
        ("node.semantics.summary = (f\"Function executing {primary_purpose.lower()}.\", 0.6)", "node.semantics.summary = (f\"Function executing {primary_purpose.lower()}.\", 0.6)\n                context.add_provenance('summary', 'SummaryEnricher', 0.6, 'Function format rule')")
    ],
    "risk.py": [
        ("context.node.metrics.risk_level = (\"High\", 0.7)", "context.node.metrics.risk_level = (\"High\", 0.7)\n            context.add_provenance('risk_level', 'RiskEnricher', 0.7, 'TODO count > 5')"),
        ("context.node.metrics.risk_level = (\"Medium\", 0.7)", "context.node.metrics.risk_level = (\"Medium\", 0.7)\n            context.add_provenance('risk_level', 'RiskEnricher', 0.7, 'TODO count > 0')"),
        ("context.node.metrics.risk_level = (\"Low\", 0.4)", "context.node.metrics.risk_level = (\"Low\", 0.4)\n            context.add_provenance('risk_level', 'RiskEnricher', 0.4, 'No TODOs found')")
    ],
    "dependencies.py": [
        ("context.node.relationships.dependencies.extend(deps)", "context.node.relationships.dependencies.extend(deps)\n                context.add_provenance('dependencies', 'DependencyEnricher', 0.8, 'Derived from SKG import edges')")
    ]
}

for filename, pairs in replacements.items():
    filepath = os.path.join("c:/Users/kumar/project/codeAtlas", enrichers_dir, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    for search, replace in pairs:
        if replace not in content:
            content = content.replace(search, replace)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
