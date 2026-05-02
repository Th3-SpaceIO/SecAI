import re
from typing import List, Dict, Any, Set

class SecurityEntityExtractor:
    """Extracts cybersecurity-specific entities using Regex and NLP patterns."""
    
    def __init__(self):
        # Compiled regex patterns for common security entities
        self.patterns = {
            "CVE": r"CVE-\d{4}-\d{4,7}",
            "CWE": r"CWE-\d{1,4}",
            "IP_ADDRESS": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
            "URL": r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+",
            "MITRE_ATTACK": r"T\d{4}(?:\.\d{3})?",  # Techniques like T1059.001
            "FILE_PATH": r"(?:[a-zA-Z]:\\|[ /])[\w.\-/ ]+\.(?:exe|dll|sys|bin|sh|py|txt|pdf)",
        }

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extracts all entities from text and returns them categorized."""
        extracted = {}
        
        for entity_type, pattern in self.patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Deduplicate while preserving order
                extracted[entity_type] = list(dict.fromkeys(matches))
                
        # Additional logic for potential tool names or product versions could go here
        # (e.g., using spaCy NER or LLM-based extraction)
        
        return extracted

    def get_relationships(self, entities: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """
        Heuristic-based relationship extraction.
        Example: If a CVE and a Tool are in the same chunk, they might be related.
        """
        relationships = []
        
        # Simplified logic: link everything to the parent document context
        # In a real KG, we would use an LLM to confirm the nature of the relationship
        
        cves = entities.get("CVE", [])
        attacks = entities.get("MITRE_ATTACK", [])
        
        for cve in cves:
            for attack in attacks:
                relationships.append({
                    "source": cve,
                    "source_type": "VULNERABILITY",
                    "target": attack,
                    "target_type": "TECHNIQUE",
                    "type": "EXPLOITED_BY"
                })
                
        return relationships
