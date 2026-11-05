"""Defer unavailable optional vLLM imports without changing any retrieval function."""
from pathlib import Path
import subprocess

root=Path('/home/nigel/acl2027')
source=root/'vendor/Tempo'
target=root/'vendor/Tempo-repaired'
if not target.exists():
    subprocess.run(['git','-C',str(source),'worktree','add','-b','tempo-repaired',str(target),'8731487254e0988eaf2ca4ae3e93ff587fec64d0'],check=True)
path=target/'retrievers.py'
body=path.read_text()
replacement='''try:
    from vllm import LLM, PoolingParams, SamplingParams
except ModuleNotFoundError:
    def _missing_vllm(*args, **kwargs):
        raise ImportError("This optional retriever requires vllm; BM25 does not use it")
    LLM = PoolingParams = SamplingParams = _missing_vllm'''
if 'def _missing_vllm' not in body:
    body=body.replace('from vllm import LLM, PoolingParams, SamplingParams\n',replacement+'\n',1)
    body=body.replace('from vllm.transformers_utils.tokenizer import get_tokenizer as get_vllm_tokenizer\n','try:\n    from vllm.transformers_utils.tokenizer import get_tokenizer as get_vllm_tokenizer\nexcept ModuleNotFoundError:\n    get_vllm_tokenizer = _missing_vllm\n',1)
path.write_text(body)
subprocess.run(['git','-C',str(target),'add','retrievers.py'],check=True)
if subprocess.run(['git','-C',str(target),'diff','--cached','--quiet']).returncode:
    subprocess.run(['git','-C',str(target),'-c','user.name=ACL Research Setup','-c','user.email=research@localhost','commit','-m','Allow CPU retrievers when optional vLLM backend is absent'],check=True)
(root/'reports/tempo_repair.patch').write_bytes(subprocess.check_output(['git','-C',str(target),'diff','8731487254e0988eaf2ca4ae3e93ff587fec64d0','HEAD']))
print('Optional-import repair committed; native retrieval functions unchanged.')
