"""
Main public API for webmetic-utm-referrer-attribution-parser.

Provides the simple, branded webmetic_referrer() function for easy attribution analysis.
"""

from typing import Dict, Optional
from .parser import parse_attribution


def webmetic_referrer(url: str, referrer: Optional[str] = None) -> Dict[str, Optional[str]]:
    """
    Analyze URL and referrer to extract complete attribution data.
    
    This is the main function for webmetic-utm-referrer-attribution-parser.
    Simply pass a destination URL and optionally a referrer URL to get
    comprehensive attribution analysis including UTM parameters, click IDs,
    and intelligent source/medium detection.
    
    Args:
        url: Destination URL with potential tracking parameters
        referrer: Optional referrer URL for additional context
        
    Returns:
        Dictionary containing complete attribution data:
        
        Core Attribution:
        - source: Final attributed source (e.g., 'google', 'facebook', '(direct)')
        - medium: Final attributed medium (e.g., 'cpc', 'organic', 'social')
        - campaign: Campaign name from UTM parameters
        - term: Search term or UTM term
        - content: UTM content parameter
        
        Tracking Parameters (only included if present):
        - All UTM parameters (utm_source, utm_medium, etc.)
        - Google Ads: gclid, gbraid, wbraid, gad_source, srsltid
        - Social Media: fbclid, ttclid, twclid, li_fat_id, igshid, ScCid
        - Email: mc_cid, mc_eid, ml_subscriber_hash
        - Other: msclkid, dclid, yclid, epik, rdt_cid, and 15+ more
        
    Examples:
        >>> # Google Ads click
        >>> result = webmetic_referrer(
        ...     url="https://site.com?utm_source=google&gclid=abc123",
        ...     referrer="https://www.google.com/aclk"
        ... )
        >>> print(result['source'])  # 'google'
        >>> print(result['gclid'])   # 'abc123'
        
        >>> # Organic search (just referrer analysis)
        >>> result = webmetic_referrer(
        ...     url="https://site.com/blog",
        ...     referrer="https://www.google.com/search?q=analytics"
        ... )
        >>> print(result['source'])  # 'Google'
        >>> print(result['term'])    # 'analytics'
        
        >>> # Direct traffic (no referrer)
        >>> result = webmetic_referrer("https://site.com")
        >>> print(result['source'])  # '(direct)'
        >>> print(result['medium'])  # '(none)'
    """
    # Build tracking_data dictionary from simple parameters
    tracking_data = {
        'dl': url or '',
        'dr': referrer or '',
        'bu': _extract_base_url(url) if url else ''
    }

    # Use existing parse_attribution logic
    raw_result = parse_attribution(tracking_data)

    # Clean up and format the result for the public API
    return _format_webmetic_result(raw_result)


def _extract_base_url(url: str) -> str:
    """Extract base URL from full URL."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    except Exception:
        return ''


def _format_webmetic_result(raw_result: Dict) -> Dict[str, Optional[str]]:
    """
    Format raw parse_attribution result into clean webmetic_referrer format.
    
    Focuses on the most important attribution data and includes all detected
    tracking parameters without the internal metadata.
    """
    result = {}

    # Core attribution (always present)
    result['source'] = raw_result.get('attribution_source')
    result['medium'] = raw_result.get('attribution_medium')
    result['campaign'] = raw_result.get('utm_campaign')
    result['term'] = (
        raw_result.get('attribution_term') or
        raw_result.get('utm_term') or
        raw_result.get('referrer_term')
    )
    result['content'] = raw_result.get('utm_content')
    result['id'] = raw_result.get('utm_id')

    # Add all detected tracking parameters
    tracking_params = [
        # UTM parameters
        'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'utm_id',

        # Google Ads
        'gclid', 'gclsrc', 'gbraid', 'wbraid', 'gad_source', 'srsltid',

        # Social Media
        'fbclid', 'ttclid', 'twclid', 'li_fat_id', 'igshid', 'sccid',

        # Microsoft
        'msclkid',

        # Email Marketing
        'mc_cid', 'mc_eid', 'ml_subscriber_hash',

        # Other Platforms
        'dclid', 'yclid', 'epik', 'ttd_uuid', 'rdt_cid', 'obOrigUrl',
        'obclick_id', 'tblci', 'irclid',

        # Analytics
        'pk_campaign', 'pk_source', 'pk_medium'
    ]

    # Only include tracking parameters that are actually present
    for param in tracking_params:
        if param in raw_result and raw_result[param]:
            result[param] = raw_result[param]

    # Remove None values for cleaner output
    return {k: v for k, v in result.items() if v is not None}


# Convenience alias for even shorter usage
referrer = webmetic_referrer
