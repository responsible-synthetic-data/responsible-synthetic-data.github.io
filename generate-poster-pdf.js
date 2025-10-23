const puppeteer = require('puppeteer');
const path = require('path');

async function generatePosterPDF() {
    console.log('🚀 Starting PDF generation...');
    
    const browser = await puppeteer.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    
    // Set viewport for consistent rendering
    await page.setViewport({
        width: 794,  // A4 width in pixels at 96 DPI
        height: 1123, // A4 height in pixels at 96 DPI
        deviceScaleFactor: 2
    });
    
    // Load the HTML file
    const htmlPath = path.join(__dirname, 'poster.html');
    await page.goto(`file://${htmlPath}`, {
        waitUntil: 'networkidle0'
    });
    
    console.log('📄 Loaded poster HTML, generating PDF...');
    
    // Generate PDF with A4 dimensions
    const pdf = await page.pdf({
        path: 'AAAI26-Workshop-Poster.pdf',
        format: 'A4',
        printBackground: true,
        margin: {
            top: '0mm',
            right: '0mm',
            bottom: '0mm',
            left: '0mm'
        }
    });
    
    console.log('✅ PDF generated successfully: AAAI26-Workshop-Poster.pdf');
    
    await browser.close();
}

// Run the function
generatePosterPDF().catch(console.error);
