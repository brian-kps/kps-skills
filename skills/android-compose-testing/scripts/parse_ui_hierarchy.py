#!/usr/bin/env python3
"""
Parse Android UI hierarchy XML to find elements by text, resource-id, or content-desc.
Outputs coordinates and bounds for tapping.
"""
import xml.etree.ElementTree as ET
import sys
import json
from typing import List, Dict, Optional

def parse_bounds(bounds_str: str) -> Dict[str, int]:
    """Parse bounds string like '[0,0][1080,2340]' into dict with x, y, width, height."""
    parts = bounds_str.replace('[', '').replace(']', ',').split(',')
    x1, y1, x2, y2 = map(int, parts[:4])
    return {
        'x1': x1,
        'y1': y1,
        'x2': x2,
        'y2': y2,
        'center_x': (x1 + x2) // 2,
        'center_y': (y1 + y2) // 2,
        'width': x2 - x1,
        'height': y2 - y1
    }

def find_elements(xml_path: str, text: Optional[str] = None, 
                 resource_id: Optional[str] = None, 
                 content_desc: Optional[str] = None,
                 class_name: Optional[str] = None) -> List[Dict]:
    """
    Find UI elements matching the given criteria.
    Returns list of dicts with element info including tap coordinates.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    matches = []
    
    def search_node(node):
        # Check if this node matches
        match = True
        if text is not None and node.get('text', '').lower() != text.lower():
            match = False
        if resource_id is not None and resource_id not in node.get('resource-id', ''):
            match = False
        if content_desc is not None and content_desc not in node.get('content-desc', ''):
            match = False
        if class_name is not None and class_name not in node.get('class', ''):
            match = False
            
        if match and (text or resource_id or content_desc or class_name):
            bounds = parse_bounds(node.get('bounds', '[0,0][0,0]'))
            matches.append({
                'text': node.get('text', ''),
                'resource_id': node.get('resource-id', ''),
                'content_desc': node.get('content-desc', ''),
                'class': node.get('class', ''),
                'clickable': node.get('clickable', 'false') == 'true',
                'enabled': node.get('enabled', 'false') == 'true',
                'bounds': bounds,
                'tap_x': bounds['center_x'],
                'tap_y': bounds['center_y']
            })
        
        # Recurse to children
        for child in node:
            search_node(child)
    
    search_node(root)
    return matches

def main():
    if len(sys.argv) < 3:
        print("Usage: parse_ui_hierarchy.py <xml_path> <search_type> <search_value>")
        print("  search_type: text|resource_id|content_desc|class")
        print("  search_value: value to search for")
        print("\nExample: parse_ui_hierarchy.py /tmp/ui.xml text 'Login'")
        sys.exit(1)
    
    xml_path = sys.argv[1]
    search_type = sys.argv[2]
    search_value = sys.argv[3]
    
    kwargs = {}
    if search_type == 'text':
        kwargs['text'] = search_value
    elif search_type == 'resource_id':
        kwargs['resource_id'] = search_value
    elif search_type == 'content_desc':
        kwargs['content_desc'] = search_value
    elif search_type == 'class':
        kwargs['class_name'] = search_value
    else:
        print(f"Unknown search type: {search_type}")
        sys.exit(1)
    
    matches = find_elements(xml_path, **kwargs)
    
    if not matches:
        print(f"No elements found matching {search_type}='{search_value}'")
        sys.exit(1)
    
    # Output as JSON
    print(json.dumps(matches, indent=2))

if __name__ == '__main__':
    main()
