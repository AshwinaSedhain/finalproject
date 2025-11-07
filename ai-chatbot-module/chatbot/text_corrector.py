# chatbot/text_corrector.py
"""
Text Correction Module
Fixes common typos and spelling errors in LLM-generated responses
"""

import re
from typing import Dict

class TextCorrector:
    """Fixes common typos and spelling errors in text."""
    
    def __init__(self):
        # Common LLM typos and their corrections
        self.common_fixes = {
            # Common word boundary typos
            r'\bTe\s+': 'The ',
            r'\bte\s+': 'the ',
            r'\bTh\s+': 'The ',  # Fix "Th " -> "The " (e.g., "Th AI service")
            r'\bhllo\b': 'hello',
            r'\bmamy\b': 'many',
            r'\bteh\b': 'the',
            r'\bth\s+': 'the ',
            r'\bwiht\b': 'with',
            r'\btaht\b': 'that',
            r'\btha\b': 'the',
            r'\bhte\b': 'the',
            r'\bthier\b': 'their',
            r'\brecieve\b': 'receive',
            r'\bseperate\b': 'separate',
            r'\boccured\b': 'occurred',
            r'\bdefinately\b': 'definitely',
            r'\bneccessary\b': 'necessary',
            r'\baccross\b': 'across',
            r'\bacheive\b': 'achieve',
            r'\bexistance\b': 'existence',
            r'\bexistant\b': 'existent',
            r'\bexistance\b': 'existence',
        }
        
        # Common sentence start fixes
        self.sentence_start_fixes = {
            r'^Te\s+': 'The ',
            r'^te\s+': 'The ',
            r'^Th\s+': 'The ',  # Fix "Th " at sentence start -> "The "
        }
        
        print("✓ Text Corrector initialized.")
    
    def fix_common_typos(self, text: str) -> str:
        """
        Fix common typos in text while preserving formatting and structure.
        """
        if not text or not isinstance(text, str):
            return text
        
        # Work on the text
        corrected = text
        
        # Fix sentence start errors
        for pattern, replacement in self.sentence_start_fixes.items():
            corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE | re.MULTILINE)
        
        # Fix common word typos (case-insensitive but preserve case)
        for pattern, replacement in self.common_fixes.items():
            # Try to preserve case
            def replace_with_case(match):
                matched = match.group(0)
                # If it's capitalized, capitalize replacement
                if matched[0].isupper():
                    return replacement.capitalize() if len(replacement) > 0 else replacement
                return replacement
            
            corrected = re.sub(pattern, replace_with_case, corrected, flags=re.IGNORECASE)
        
        # Fix common spacing issues
        corrected = re.sub(r'\s+', ' ', corrected)  # Multiple spaces
        corrected = re.sub(r'\s+([.,!?;:])', r'\1', corrected)  # Space before punctuation
        corrected = re.sub(r'([.,!?;:])([^\s])', r'\1 \2', corrected)  # Space after punctuation
        
        # Fix common word boundary issues
        corrected = re.sub(r'\b(\w+)\s+(\w+)\b', self._fix_word_boundary, corrected)
        
        return corrected.strip()
    
    def _fix_word_boundary(self, match) -> str:
        """Helper to fix word boundary issues."""
        word1, word2 = match.groups()
        
        # Common two-word fixes
        two_word_fixes = {
            ('te', 'sales'): 'the sales',
            ('Te', 'sales'): 'The sales',
            ('te', 'data'): 'the data',
            ('Te', 'data'): 'The data',
        }
        
        key = (word1, word2)
        if key in two_word_fixes:
            return two_word_fixes[key]
        
        return match.group(0)
    
    def fix_llm_response(self, response: str) -> str:
        """
        Comprehensive fix for LLM-generated responses.
        """
        if not response:
            return response
        
        corrected = response
        
        # IMMEDIATE FIX: Fix "Te " -> "The " at the very start (before any other processing)
        # This is the most critical fix to prevent "Te AI service", "Te customer" errors
        # Fix common patterns first - COMPREHENSIVE FIXES - MULTIPLE PASSES TO ENSURE CATCHING ALL
        
        # PASS 1: Fix "Al" -> "AI" FIRST (before fixing "Te")
        corrected = corrected.replace('Al service', 'AI service')
        corrected = corrected.replace('al service', 'AI service')
        corrected = corrected.replace('AL service', 'AI service')
        # Fix "Al" when it's clearly meant to be "AI" (context-dependent)
        corrected = re.sub(r'\bAl\s+service\b', 'AI service', corrected, flags=re.IGNORECASE)
        corrected = re.sub(r'\bThe\s+Al\b', 'The AI', corrected, flags=re.IGNORECASE)
        corrected = re.sub(r'\bthe\s+Al\b', 'the AI', corrected, flags=re.IGNORECASE)
        
        # PASS 2: Fix "Te Al" -> "The AI" (common LLM typo where both are wrong)
        corrected = corrected.replace('Te Al', 'The AI')
        corrected = corrected.replace('Te al', 'The AI')
        corrected = corrected.replace('te Al', 'The AI')
        corrected = corrected.replace('TE Al', 'The AI')
        corrected = corrected.replace('Te AL', 'The AI')
        corrected = corrected.replace('TE AL', 'The AI')
        corrected = corrected.replace('Te Al service', 'The AI service')
        corrected = corrected.replace('Te al service', 'The AI service')
        corrected = corrected.replace('te Al service', 'The AI service')
        
        # PASS 3: Fix "Te AI" -> "The AI" (when AI is correct but "Te" is wrong)
        corrected = corrected.replace('Te AI', 'The AI')
        corrected = corrected.replace('Te ai', 'The AI')
        corrected = corrected.replace('te AI', 'The AI')
        corrected = corrected.replace('TE AI', 'The AI')
        corrected = corrected.replace('Te AI service', 'The AI service')
        corrected = corrected.replace('Te ai service', 'The AI service')
        
        # PASS 4: Fix "Te " followed by any word (most aggressive)
        corrected = corrected.replace('Te customer', 'The customer')
        corrected = corrected.replace('Te top', 'The top')
        corrected = corrected.replace('Te sales', 'The sales')
        corrected = corrected.replace('Te data', 'The data')
        corrected = corrected.replace('Te following', 'The following')
        corrected = corrected.replace('Te chart', 'The chart')
        corrected = corrected.replace('Te table', 'The table')
        corrected = corrected.replace('Te results', 'The results')
        corrected = corrected.replace('Te analysis', 'The analysis')
        
        # PASS 5: Regex fixes for word boundaries - catch "Te " followed by any capitalized word
        corrected = re.sub(r'\bTe\s+([A-Z][a-z]+)', r'The \1', corrected)
        corrected = re.sub(r'\bTe\s+AI\b', 'The AI', corrected, flags=re.IGNORECASE)
        corrected = re.sub(r'\bTe\s+Al\b', 'The AI', corrected, flags=re.IGNORECASE)
        # Fix at sentence start
        corrected = re.sub(r'^Te\s+', 'The ', corrected, flags=re.MULTILINE)
        # Fix after punctuation
        corrected = re.sub(r'([.!?]\s+)Te\s+', r'\1The ', corrected, flags=re.MULTILINE)
        
        # PRIORITY FIX: Fix "Th " -> "The " immediately (most common after "hllo")
        # This needs to be done before other fixes to catch it early
        # Multiple patterns to catch all variations
        # Direct string replacements first (fastest)
        corrected = corrected.replace('Th AI', 'The AI')
        corrected = corrected.replace('Th ai', 'The AI')
        corrected = corrected.replace('Th customer', 'The customer')
        corrected = corrected.replace('Th AI service', 'The AI service')
        # Then regex patterns for word boundaries
        corrected = re.sub(r'\bTh\s+', 'The ', corrected)  # Word boundary
        corrected = re.sub(r'^Th\s+', 'The ', corrected, flags=re.MULTILINE)  # Start of line
        corrected = re.sub(r'([.!?]\s+)Th\s+', r'\1The ', corrected)  # After punctuation
        # Also handle "Th AI" specifically (common pattern) - case insensitive
        corrected = re.sub(r'\bTh\s+AI\b', 'The AI', corrected, flags=re.IGNORECASE)
        # Final fallback: direct string replacement for any remaining cases
        corrected = corrected.replace('Th AI', 'The AI').replace('Th ai', 'The AI')
        # Fix at start of string
        if corrected.startswith('Th '):
            corrected = 'The ' + corrected[3:]
        
        # CRITICAL FIXES: Fix the most common LLM typos first (in priority order)
        
        # 1. Fix "hllo" -> "hello" FIRST (most common issue) - COMPREHENSIVE FIX
        # Use case-insensitive replacement first, then handle capitalization
        # This catches ALL variations: hllo, Hllo, HLLO, etc.
        def replace_hllo(match):
            word = match.group(0)
            # If it starts with capital, return "Hello", otherwise "hello"
            if word[0].isupper():
                return 'Hello' + (word[4:] if len(word) > 4 else '')
            else:
                return 'hello' + (word[4:] if len(word) > 4 else '')
        
        # Replace all instances of "hllo" (case-insensitive) at word boundaries
        corrected = re.sub(r'\bhllo\b', replace_hllo, corrected, flags=re.IGNORECASE)
        
        # Also handle cases where it might not have word boundaries (edge cases)
        # This catches "hllo" even when not at word boundaries
        def replace_hllo_no_boundary(match):
            prefix = match.group(1)
            hllo_word = 'hllo'  # The matched word (case-insensitive)
            suffix = match.group(2)
            # Check if the original had capital H
            original = match.group(0)
            if len(original) > len(prefix) and original[len(prefix)].isupper():
                return prefix + 'Hello' + suffix
            else:
                return prefix + 'hello' + suffix
        
        corrected = re.sub(r'([^a-zA-Z])hllo([^a-zA-Z])', replace_hllo_no_boundary, corrected, flags=re.IGNORECASE)
        
        # Ensure "Hello" at start of sentences
        corrected = re.sub(r'^hllo\b', 'Hello', corrected, flags=re.MULTILINE | re.IGNORECASE)
        corrected = re.sub(r'([.!?]\s+)hllo\b', r'\1Hello', corrected, flags=re.IGNORECASE)
        
        # FINAL FALLBACK: Direct string replacement (case-insensitive) to catch ANY remaining instances
        # This is a last resort to ensure we catch everything
        import string
        if 'hllo' in corrected.lower():
            # Split into words and fix
            words = corrected.split()
            fixed_words = []
            for word in words:
                # Remove punctuation temporarily
                word_clean = word.strip(string.punctuation)
                if word_clean.lower() == 'hllo' and len(word_clean) > 0:
                    # Preserve capitalization
                    replacement = 'Hello' if word_clean[0].isupper() else 'hello'
                    # Restore punctuation
                    if word != word_clean:
                        # Has punctuation - find it
                        if word and word[0] in string.punctuation:
                            replacement = word[0] + replacement
                        if word and word[-1] in string.punctuation:
                            replacement = replacement + word[-1]
                    fixed_words.append(replacement)
                else:
                    fixed_words.append(word)
            corrected = ' '.join(fixed_words)
        
        # 2. Fix "Th " -> "The " FIRST (before "Te " fix)
        corrected = re.sub(r'\bTh\s+', 'The ', corrected)
        corrected = re.sub(r'^Th\s+', 'The ', corrected, flags=re.MULTILINE)
        corrected = re.sub(r'([.!?]\s+)Th\s+', r'\1The ', corrected)
        
        # 3. Fix "Te " -> "The " (case-sensitive to preserve "te" in other contexts)
        # CRITICAL: Protect "The AI" BEFORE doing any "Te " replacements
        # Use a unique placeholder that won't conflict
        protected_phrases = []
        protected_placeholder = "___THE_AI_PLACEHOLDER_{}___"
        protected_count = 0
        
        # Protect "The AI" phrases (case-insensitive)
        def protect_the_ai(match):
            nonlocal protected_count
            phrase = match.group(0)  # Original phrase (e.g., "The AI", "the AI", "THE AI")
            placeholder = protected_placeholder.format(protected_count)
            protected_phrases.append((placeholder, phrase))
            protected_count += 1
            return placeholder
        
        # Protect "The AI" in various contexts BEFORE any replacements
        corrected = re.sub(r'\bThe\s+AI\b', protect_the_ai, corrected, flags=re.IGNORECASE)
        corrected = re.sub(r'\bthe\s+AI\b', protect_the_ai, corrected, flags=re.IGNORECASE)
        corrected = re.sub(r'\bTHE\s+AI\b', protect_the_ai, corrected)
        
        # Now fix "Te " -> "The " (this won't affect protected phrases)
        corrected = re.sub(r'\bTe\s+', 'The ', corrected)
        corrected = re.sub(r'^Te\s+', 'The ', corrected, flags=re.MULTILINE)
        
        # Restore protected phrases
        for placeholder, phrase in protected_phrases:
            corrected = corrected.replace(placeholder, phrase)
        
        # 4. Fix "te " at start of sentence (after punctuation) -> "The "
        corrected = re.sub(r'([.!?]\s+)te\s+([A-Z])', r'\1The \2', corrected)
        corrected = re.sub(r'(^|\n)te\s+([a-z])', lambda m: f'{m.group(1)}The {m.group(2)}', corrected, flags=re.MULTILINE)
        
        # 4. Fix "srry" -> "sorry" (all cases)
        corrected = re.sub(r'^Srry\b', 'Sorry', corrected, flags=re.MULTILINE)
        corrected = re.sub(r'\bSrry\b', 'Sorry', corrected)
        corrected = re.sub(r'\bsrry\b', 'sorry', corrected, flags=re.IGNORECASE)
        
        # 5. Fix "mamy" -> "many" (all cases)
        corrected = re.sub(r'\bMamy\b', 'Many', corrected)
        corrected = re.sub(r'\bmamy\b', 'many', corrected, flags=re.IGNORECASE)
        
        # Fix other common typos
        corrected = re.sub(r'\bteh\b', 'the', corrected, flags=re.IGNORECASE)
        corrected = re.sub(r'\btha\b', 'the', corrected, flags=re.IGNORECASE)
        corrected = re.sub(r'\bhte\b', 'the', corrected, flags=re.IGNORECASE)
        corrected = re.sub(r'\bwiht\b', 'with', corrected, flags=re.IGNORECASE)
        corrected = re.sub(r'\btaht\b', 'that', corrected, flags=re.IGNORECASE)
        corrected = re.sub(r'\bthier\b', 'their', corrected, flags=re.IGNORECASE)
        corrected = re.sub(r'\brecieve\b', 'receive', corrected, flags=re.IGNORECASE)
        corrected = re.sub(r'\bseperate\b', 'separate', corrected, flags=re.IGNORECASE)
        corrected = re.sub(r'\boccured\b', 'occurred', corrected, flags=re.IGNORECASE)
        corrected = re.sub(r'\bdefinately\b', 'definitely', corrected, flags=re.IGNORECASE)
        corrected = re.sub(r'\bneccessary\b', 'necessary', corrected, flags=re.IGNORECASE)
        corrected = re.sub(r'\baccross\b', 'across', corrected, flags=re.IGNORECASE)
        corrected = re.sub(r'\bacheive\b', 'achieve', corrected, flags=re.IGNORECASE)
        
        # Fix "Te sales data" -> "The sales data" (common pattern)
        # But skip if it's "Te AI" (should already be "The AI" from protection above)
        # Protect "The AI" again before this replacement
        protected_phrases2 = []
        protected_placeholder2 = "___THE_AI_PLACEHOLDER2_{}___"
        protected_count2 = 0
        
        def protect_the_ai2(match):
            nonlocal protected_count2
            phrase = match.group(0)
            placeholder = protected_placeholder2.format(protected_count2)
            protected_phrases2.append((placeholder, phrase))
            protected_count2 += 1
            return placeholder
        
        corrected = re.sub(r'\bThe\s+AI\b', protect_the_ai2, corrected, flags=re.IGNORECASE)
        
        corrected = re.sub(r'\bTe\s+(sales|data|following|chart|table|results|analysis)', 
                          lambda m: f'The {m.group(1)}', corrected, flags=re.IGNORECASE)
        
        # Restore protected phrases
        for placeholder, phrase in protected_phrases2:
            corrected = corrected.replace(placeholder, phrase)
        
        # Final safeguard: Ensure "The AI" is never changed to "Te AI" (multiple passes)
        corrected = corrected.replace('Te AI', 'The AI')
        corrected = corrected.replace('Te ai', 'The AI')
        corrected = corrected.replace('te AI', 'The AI')
        corrected = corrected.replace('TE AI', 'The AI')
        # Also fix if "The AI" somehow became "Te AI"
        corrected = re.sub(r'\bTe\s+AI\b', 'The AI', corrected, flags=re.IGNORECASE)
        
        # Fix spacing issues
        corrected = re.sub(r'\s+', ' ', corrected)  # Multiple spaces to single
        corrected = re.sub(r'\s+([.,!?;:])', r'\1', corrected)  # Remove space before punctuation
        corrected = re.sub(r'([.,!?;:])([^\s])', r'\1 \2', corrected)  # Add space after punctuation
        
        # Ensure proper capitalization after sentence endings
        corrected = re.sub(r'([.!?])\s+([a-z])', lambda m: f'{m.group(1)} {m.group(2).upper()}', corrected)
        
        # Fix capitalization at start of response
        if corrected and corrected[0].islower():
            corrected = corrected[0].upper() + corrected[1:]
        
        # Clean up extra whitespace and newlines
        corrected = re.sub(r'\n\s*\n\s*\n+', '\n\n', corrected)  # Multiple newlines
        corrected = corrected.strip()
        
        # FINAL SAFEGUARD: Fix any remaining "Te AI" variations that might have slipped through
        corrected = corrected.replace('Te AI', 'The AI')
        corrected = corrected.replace('Te ai', 'The AI')
        corrected = corrected.replace('te AI', 'The AI')
        corrected = corrected.replace('TE AI', 'The AI')
        # Fix "Tee" -> "The" (common typo)
        corrected = corrected.replace('Tee ', 'The ')
        corrected = corrected.replace('Tee customer', 'The customer')
        corrected = corrected.replace('Tee custmmer', 'The customer')
        corrected = re.sub(r'\bTee\s+', 'The ', corrected)  # Catch all "Tee " variations
        
        # CRITICAL: Fix "Te Al" -> "The AI" in final pass
        corrected = corrected.replace('Te Al', 'The AI')
        corrected = corrected.replace('Te al', 'The AI')
        corrected = corrected.replace('te Al', 'The AI')
        corrected = corrected.replace('TE Al', 'The AI')
        # Fix "Al service" -> "AI service" (when "AI" is misspelled as "Al")
        corrected = corrected.replace('Al service', 'AI service')
        corrected = corrected.replace('al service', 'AI service')
        # Fix "Al" when it should be "AI" (context-dependent, but common in "The AI service")
        corrected = re.sub(r'\bThe\s+Al\s+service\b', 'The AI service', corrected, flags=re.IGNORECASE)
        corrected = re.sub(r'\bThe\s+Al\b', 'The AI', corrected, flags=re.IGNORECASE)
        
        # Fix common word typos that appear in responses
        # Customer typos
        corrected = corrected.replace('custmmer', 'customer')
        corrected = corrected.replace('custmmers', 'customers')
        corrected = corrected.replace('custmer', 'customer')
        corrected = corrected.replace('custmers', 'customers')
        corrected = re.sub(r'\bcustmmer\b', 'customer', corrected, flags=re.IGNORECASE)
        corrected = re.sub(r'\bcustmmers\b', 'customers', corrected, flags=re.IGNORECASE)
        corrected = re.sub(r'\bcustmer\b', 'customer', corrected, flags=re.IGNORECASE)
        corrected = re.sub(r'\bcustmers\b', 'customers', corrected, flags=re.IGNORECASE)
        
        # February typos
        corrected = corrected.replace('Februrry', 'February')
        corrected = corrected.replace('Februry', 'February')
        corrected = re.sub(r'\bFebrurry\b', 'February', corrected, flags=re.IGNORECASE)
        corrected = re.sub(r'\bFebrury\b', 'February', corrected, flags=re.IGNORECASE)
        
        # Promotion typos
        corrected = corrected.replace('promtions', 'promotions')
        corrected = corrected.replace('promtion', 'promotion')
        corrected = re.sub(r'\bpromtions\b', 'promotions', corrected, flags=re.IGNORECASE)
        corrected = re.sub(r'\bpromtion\b', 'promotion', corrected, flags=re.IGNORECASE)
        
        # Further typos
        corrected = corrected.replace('frrther', 'further')
        corrected = corrected.replace('furrther', 'further')
        corrected = re.sub(r'\bfrrther\b', 'further', corrected, flags=re.IGNORECASE)
        corrected = re.sub(r'\bfurrther\b', 'further', corrected, flags=re.IGNORECASE)
        
        # Substantial typos
        corrected = corrected.replace('uubstantia', 'substantial')
        corrected = corrected.replace('uubstantial', 'substantial')
        corrected = re.sub(r'\buubstantia\w*\b', 'substantial', corrected, flags=re.IGNORECASE)
        
        # ULTIMATE FIX: Catch "Te " followed by ANY word (most aggressive fix)
        # This ensures we catch ALL instances of "Te " at word boundaries
        # MULTIPLE PASSES to ensure we catch everything
        for _ in range(3):  # Run 3 times to catch nested/overlapping patterns
            corrected = re.sub(r'\bTe\s+', 'The ', corrected)
            corrected = re.sub(r'^Te\s+', 'The ', corrected, flags=re.MULTILINE)
            corrected = re.sub(r'([.!?]\s+)Te\s+', r'\1The ', corrected, flags=re.MULTILINE)
            # Also fix "Al" -> "AI" in multiple passes
            corrected = re.sub(r'\bThe\s+Al\b', 'The AI', corrected, flags=re.IGNORECASE)
            corrected = re.sub(r'\bAl\s+service\b', 'AI service', corrected, flags=re.IGNORECASE)
        
        # FINAL VERIFICATION: One more comprehensive pass
        # Fix any remaining "Te" patterns
        corrected = corrected.replace('Te ', 'The ')
        # Fix any remaining "Al" that should be "AI" (context-aware)
        # Only fix "Al" when it's clearly in AI-related contexts
        corrected = re.sub(r'\bThe\s+Al\b', 'The AI', corrected, flags=re.IGNORECASE)
        corrected = re.sub(r'\bAl\s+service\b', 'AI service', corrected, flags=re.IGNORECASE)
        corrected = re.sub(r'\bAl\s+is\b', 'AI is', corrected, flags=re.IGNORECASE)
        corrected = re.sub(r'\bAl\s+can\b', 'AI can', corrected, flags=re.IGNORECASE)
        # Don't replace standalone "Al" as it might be a name or abbreviation
        
        return corrected

