# OWASP Top 10 for LLM Applications v1.1

## LLM01: Prompt Injection
This vulnerability occurs when an attacker manipulates an LLM's output through crafted inputs. 
- **Direct Injections:** Overwriting system prompts.
- **Indirect Injections:** The LLM retrieves malicious content from an external source (like a RAG knowledge base).

## LLM02: Insecure Output Handling
Occurs when an LLM output is accepted without scrutiny, potentially leading to XSS, CSRF, or SSRF in downstream systems.

## LLM06: Sensitive Information Disclosure
LLMs may inadvertently reveal confidential data, proprietary algorithms, or PII through their responses. RAG systems are particularly vulnerable if access controls are not enforced at the retrieval layer.
