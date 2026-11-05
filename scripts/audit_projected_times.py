"""Count actual parsed time availability using the gold-free baseline inputs."""
from pathlib import Path
import json

inputs=Path('/home/acl-infer/inputs')
report=[]
for path in sorted(inputs.glob('baseline-*-bm25-*/input.json')):
    d=json.loads(path.read_text())
    report.append({'run_id':path.parent.name,'domain':d['domain'],'queries':len(d['queries']),'documents':len(d['ids']),'parsed_document_insert_time':sum(x is not None for x in d['dit']),'parsed_document_event_time':sum(x is not None for x in d['det']),'parsed_query_insert_time':sum(q['qit'] is not None for q in d['queries']),'parsed_or_query_extracted_event_time':sum(q['qet'] is not None for q in d['queries'])})
Path('/home/nigel/acl2027/reports/temporal_metadata_audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
