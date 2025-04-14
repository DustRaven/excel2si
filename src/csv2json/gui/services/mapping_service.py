"""
Mapping service for the CSV2JSON converter GUI.
"""

from src.csv2json.core.logging import logger


class MappingService:
    """
    Service for handling field mapping operations.
    """
    
    def __init__(self):
        # Common word variations to handle
        self.variations = {
            'address': ['adresse', 'addr', 'adr'],
            'street': ['strasse', 'straße', 'str'],
            'city': ['stadt', 'ort', 'place'],
            'zip': ['zipcode', 'postal', 'postcode', 'plz', 'postleitzahl', 'zip_code', 'postal_code'],
            'plz': ['zip', 'zipcode', 'postal', 'postcode', 'postleitzahl', 'zip_code', 'postal_code'],
            'name': ['nom', 'namen'],
            'first': ['vorname', 'firstname', 'first_name', 'given'],
            'last': ['nachname', 'lastname', 'last_name', 'surname', 'family'],
            'phone': ['telefon', 'tel', 'telephone', 'mobile', 'cell'],
            'email': ['e-mail', 'mail', 'e_mail'],
            'country': ['land', 'pays', 'nation'],
            'state': ['bundesland', 'province', 'region'],
            'company': ['firma', 'organization', 'organisation', 'business'],
            'date': ['datum', 'day', 'tag'],
            'number': ['nummer', 'no', 'num', 'nr'],
            'price': ['preis', 'cost', 'prix'],
            'amount': ['betrag', 'sum', 'quantity', 'menge']
        }
        
        # Special cases for common field names
        self.special_cases = {
            'zip_code': ['PLZ', 'ZIP', 'PostalCode'],
            'address': ['Adresse', 'Anschrift', 'ADRESSE'],
            'city': ['Stadt', 'Ort', 'CITY'],
            'country': ['Land', 'COUNTRY'],
            'phone': ['Telefon', 'Tel', 'PHONE'],
            'email': ['Email', 'E-Mail', 'EMAIL']
        }
        
        # Create a reverse lookup for variations (case-insensitive)
        self.variation_lookup = {}
        for main, variants in self.variations.items():
            for variant in variants:
                self.variation_lookup[variant.lower()] = main
            self.variation_lookup[main.lower()] = main
    
    def auto_map_fields(self, target_fields, source_fields):
        """
        Automatically map fields based on name similarity.
        
        Args:
            target_fields (list): List of target field names
            source_fields (list): List of source field names
            
        Returns:
            dict: Mapping from target fields to source fields
        """
        logger.info("Starting auto-mapping of fields")
        logger.info(f"Target fields: {target_fields}")
        logger.info(f"Source fields: {source_fields}")
        
        # Create a mapping based on matches
        mapping = {}
        for target in target_fields:
            # Try to find an exact match
            if target in source_fields:
                mapping[target] = target
                logger.info(f"Exact match: {target}")
                continue
            
            # Try to find a case-insensitive match
            target_lower = target.lower()
            exact_match_found = False
            
            for source in source_fields:
                if target_lower == source.lower():
                    mapping[target] = source
                    logger.info(f"Case-insensitive match: {target} -> {source}")
                    exact_match_found = True
                    break
            
            if exact_match_found:
                continue
            
            # Try to match based on word variations
            best_match = None
            best_score = 0
            logger.info(f"Trying to fuzzy match: {target}")
            
            # Extract the base words from target (remove _id, _name suffixes)
            target_base = target_lower
            for suffix in ['_id', '_name', '_nr', '_no', '_num', '_number']:
                if target_base.endswith(suffix):
                    target_base = target_base[:-len(suffix)]
                    logger.debug(f"Removed suffix from {target_lower} -> {target_base}")
                    break
            
            # Check if any part of the target matches a known variation
            target_parts = target_base.split('_')
            target_variations = set()
            
            for part in target_parts:
                # Add the original part
                target_variations.add(part)
                # Add any known variations (case-insensitive)
                if part.lower() in self.variation_lookup:
                    variation = self.variation_lookup[part.lower()]
                    target_variations.add(variation)
                    logger.debug(f"Found variation for '{part}': '{variation}'")
            
            logger.debug(f"Target variations for {target}: {target_variations}")
            
            for source in source_fields:
                source_lower = source.lower()
                source_base = source_lower
                
                # Extract the base words from source
                for suffix in ['_id', '_name', '_nr', '_no', '_num', '_number']:
                    if source_base.endswith(suffix):
                        source_base = source_base[:-len(suffix)]
                        logger.debug(f"Removed suffix from {source_lower} -> {source_base}")
                        break
                
                # Split source into parts
                source_parts = source_base.split('_')
                source_variations = set()
                
                # Check for special case matches
                if target_lower in self.special_cases and source in self.special_cases[target_lower]:
                    logger.info(f"Special case match: {target} -> {source}")
                    best_match = source
                    best_score = 1.0
                    break
                
                # Check for direct match with known variations
                if target_base in self.variations and source.lower() in [v.lower() for v in self.variations[target_base]] or \
                   source_base in self.variations and target.lower() in [v.lower() for v in self.variations[source_base]]:
                    logger.info(f"Direct variation match: {target} -> {source}")
                    best_match = source
                    best_score = 0.9
                    break
                
                for part in source_parts:
                    # Add the original part
                    source_variations.add(part)
                    # Add any known variations (case-insensitive)
                    if part.lower() in self.variation_lookup:
                        variation = self.variation_lookup[part.lower()]
                        source_variations.add(variation)
                        logger.debug(f"Found source variation for '{part}': '{variation}'")
                
                # Calculate similarity score based on common variations
                common_variations = target_variations.intersection(source_variations)
                if common_variations:
                    logger.debug(f"Common variations between {target} and {source}: {common_variations}")
                    score = len(common_variations) / max(len(target_variations), len(source_variations))
                    
                    # Boost score for longer matches
                    if len(common_variations) > 1:
                        score *= 1.5
                    
                    logger.debug(f"Score for {target} -> {source}: {score:.2f}")
                    
                    if score > best_score:
                        best_score = score
                        best_match = source
            
            # If we found a good match (score > 0.3), use it - lowered threshold for more matches
            if best_match and best_score > 0.3:
                mapping[target] = best_match
                logger.info(f"Fuzzy matched: {target} -> {best_match} (score: {best_score:.2f})")
        
        logger.info(f"Auto-mapping completed with {len(mapping)} matches")
        return mapping
