#!/usr/bin/env python3
"""
High-quality HTML to PDF converter for poster.html
Supports multiple conversion methods with optimized settings for print quality.
"""

import os
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any
import argparse


def convert_with_selenium(html_file: str, output_file: str, **kwargs) -> bool:
    """
    Convert HTML to PDF using Selenium with Chrome (most reliable on macOS)
    
    Args:
        html_file: Path to HTML file
        output_file: Path to output PDF file
        **kwargs: Additional options
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        import json
        import base64
        
        # Chrome options for PDF generation
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-images')
        chrome_options.add_argument('--run-all-compositor-stages-before-draw')
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        
        # Initialize Chrome driver
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            # Load the HTML file
            html_path = Path(html_file).resolve().as_uri()
            driver.get(html_path)
            
            # Wait for page to load completely
            time.sleep(3)
            
            # Execute JavaScript to trigger print
            print_options = {
                'landscape': False,
                'displayHeaderFooter': False,
                'printBackground': True,
                'preferCSSPageSize': True,
                'paperWidth': 8.27,  # A4 width in inches
                'paperHeight': 11.69,  # A4 height in inches
                'marginTop': 0,
                'marginBottom': 0,
                'marginLeft': 0,
                'marginRight': 0,
                'scale': 1.0
            }
            
            # Use Chrome DevTools Protocol to generate PDF
            result = driver.execute_cdp_cmd('Page.printToPDF', print_options)
            
            # Decode and save PDF
            pdf_data = base64.b64decode(result['data'])
            with open(output_file, 'wb') as f:
                f.write(pdf_data)
            
            print(f"✅ PDF generated successfully using Selenium: {output_file}")
            return True
            
        finally:
            driver.quit()
        
    except ImportError:
        print("❌ Selenium not installed. Install with: pip install selenium")
        print("   Also requires Chrome browser to be installed")
        return False
    except Exception as e:
        print(f"❌ Selenium conversion failed: {e}")
        return False


def convert_with_weasyprint(html_file: str, output_file: str, **kwargs) -> bool:
    """
    Convert HTML to PDF using WeasyPrint (best for CSS support)
    
    Args:
        html_file: Path to HTML file
        output_file: Path to output PDF file
        **kwargs: Additional options
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        import weasyprint
        from weasyprint import HTML, CSS
        
        # High-quality PDF settings
        html_doc = HTML(filename=html_file)
        
        # Custom CSS for print optimization
        print_css = CSS(string='''
            @page {
                size: A4;
                margin: 0;
                -webkit-print-color-adjust: exact;
                color-adjust: exact;
            }
            
            body {
                -webkit-print-color-adjust: exact;
                color-adjust: exact;
            }
            
            * {
                -webkit-print-color-adjust: exact;
                color-adjust: exact;
            }
        ''')
        
        # Generate PDF with high quality settings
        html_doc.write_pdf(
            output_file,
            stylesheets=[print_css],
            optimize_images=True,
            jpeg_quality=95,
            pdf_version='1.7'
        )
        
        print(f"✅ PDF generated successfully using WeasyPrint: {output_file}")
        return True
        
    except ImportError:
        print("❌ WeasyPrint not installed. Install with: pip install weasyprint")
        return False
    except Exception as e:
        print(f"❌ WeasyPrint conversion failed: {e}")
        return False


def convert_with_pdfkit(html_file: str, output_file: str, **kwargs) -> bool:
    """
    Convert HTML to PDF using pdfkit/wkhtmltopdf (good for complex layouts)
    
    Args:
        html_file: Path to HTML file
        output_file: Path to output PDF file
        **kwargs: Additional options
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        import pdfkit
        
        # High-quality PDF options
        options = {
            'page-size': 'A4',
            'margin-top': '0',
            'margin-right': '0',
            'margin-bottom': '0',
            'margin-left': '0',
            'encoding': "UTF-8",
            'no-outline': None,
            'enable-local-file-access': None,
            'print-media-type': None,
            'disable-smart-shrinking': None,
            'dpi': 300,
            'image-quality': 100,
            'image-dpi': 300,
            'lowquality': False,
            'zoom': 1.0,
            'viewport-size': '1280x1024',
            'javascript-delay': 1000,
            'load-error-handling': 'ignore',
            'load-media-error-handling': 'ignore'
        }
        
        # Update with any custom options
        options.update(kwargs.get('pdfkit_options', {}))
        
        pdfkit.from_file(html_file, output_file, options=options)
        
        print(f"✅ PDF generated successfully using pdfkit: {output_file}")
        return True
        
    except ImportError:
        print("❌ pdfkit not installed. Install with: pip install pdfkit")
        print("   Also requires wkhtmltopdf: https://wkhtmltopdf.org/downloads.html")
        return False
    except Exception as e:
        print(f"❌ pdfkit conversion failed: {e}")
        return False


def convert_with_playwright(html_file: str, output_file: str, **kwargs) -> bool:
    """
    Convert HTML to PDF using Playwright (modern browser engine)
    
    Args:
        html_file: Path to HTML file
        output_file: Path to output PDF file
        **kwargs: Additional options
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            
            # Load the HTML file
            html_path = Path(html_file).resolve().as_uri()
            page.goto(html_path)
            
            # Wait for any animations or dynamic content
            page.wait_for_timeout(2000)
            
            # High-quality PDF options
            pdf_options = {
                'path': output_file,
                'format': 'A4',
                'margin': {'top': '0', 'right': '0', 'bottom': '0', 'left': '0'},
                'print_background': True,
                'prefer_css_page_size': True,
                'scale': 1.0
            }
            
            # Update with any custom options
            pdf_options.update(kwargs.get('playwright_options', {}))
            
            page.pdf(**pdf_options)
            browser.close()
            
        print(f"✅ PDF generated successfully using Playwright: {output_file}")
        return True
        
    except ImportError:
        print("❌ Playwright not installed. Install with: pip install playwright")
        print("   Then run: playwright install chromium")
        return False
    except Exception as e:
        print(f"❌ Playwright conversion failed: {e}")
        return False


def html_to_pdf(
    html_file: str,
    output_file: Optional[str] = None,
    method: str = "auto",
    **kwargs
) -> bool:
    """
    Convert HTML file to high-quality PDF
    
    Args:
        html_file: Path to HTML file
        output_file: Output PDF path (defaults to same name with .pdf extension)
        method: Conversion method ('weasyprint', 'pdfkit', 'playwright', or 'auto')
        **kwargs: Additional options for specific converters
    
    Returns:
        bool: True if successful, False otherwise
    """
    
    # Validate input file
    if not os.path.exists(html_file):
        print(f"❌ HTML file not found: {html_file}")
        return False
    
    # Set default output file
    if output_file is None:
        output_file = Path(html_file).with_suffix('.pdf')
    
    print(f"🔄 Converting {html_file} to {output_file}")
    
    # Try conversion methods
    if method == "auto":
        # Try methods in order of preference
        methods = [
            ("selenium", convert_with_selenium),
            ("playwright", convert_with_playwright),
            ("weasyprint", convert_with_weasyprint),
            ("pdfkit", convert_with_pdfkit)
        ]
        
        for method_name, converter in methods:
            print(f"🔄 Trying {method_name}...")
            if converter(html_file, output_file, **kwargs):
                return True
        
        print("❌ All conversion methods failed")
        return False
    
    elif method == "selenium":
        return convert_with_selenium(html_file, output_file, **kwargs)
    elif method == "weasyprint":
        return convert_with_weasyprint(html_file, output_file, **kwargs)
    elif method == "pdfkit":
        return convert_with_pdfkit(html_file, output_file, **kwargs)
    elif method == "playwright":
        return convert_with_playwright(html_file, output_file, **kwargs)
    else:
        print(f"❌ Unknown method: {method}")
        return False


def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(
        description="Convert HTML to high-quality PDF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python convert_to_pdf.py poster.html
  python convert_to_pdf.py poster.html -o poster.pdf
  python convert_to_pdf.py poster.html -m playwright
  python convert_to_pdf.py poster.html -m weasyprint -o high_quality.pdf
        """
    )
    
    parser.add_argument(
        'html_file',
        help='HTML file to convert'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output PDF file (default: same name as HTML with .pdf extension)'
    )
    
    parser.add_argument(
        '-m', '--method',
        choices=['auto', 'selenium', 'weasyprint', 'pdfkit', 'playwright'],
        default='auto',
        help='Conversion method (default: auto)'
    )
    
    args = parser.parse_args()
    
    success = html_to_pdf(
        html_file=args.html_file,
        output_file=args.output,
        method=args.method
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
