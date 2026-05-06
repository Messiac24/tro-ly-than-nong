import asyncio
from playwright import async_api

async def run_test():
    pw = None
    browser = None
    context = None

    try:
        # Start a Playwright session in asynchronous mode
        pw = await async_api.async_playwright().start()

        # Launch a Chromium browser in headless mode with custom arguments
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--window-size=1280,720",
                "--disable-dev-shm-usage",
                "--ipc=host"
            ],
        )

        # Create a new browser context (like an incognito window)
        context = await browser.new_context()
        context.set_default_timeout(5000)

        # Open a new page in the browser context
        page = await context.new_page()

        # -> Navigate to http://127.0.0.1:8000
        page.on("console", lambda msg: print(f"Browser console: {msg.text}"))
        await page.goto("http://127.0.0.1:8000")
        
        # -> Login as admin
        await page.goto("http://127.0.0.1:8000/login.html")
        frame = context.pages[-1]
        await asyncio.sleep(1)
        await frame.locator('#login-username').fill('admin')
        await frame.locator('#login-password').fill('admin123')
        await frame.locator('#login-form button[type="submit"]').click()
        await asyncio.sleep(2)
        
        # Open admin dashboard
        await page.goto("http://127.0.0.1:8000/admin.html")
        
        # Setup dialog handler to auto-accept alerts and capture their messages
        dialog_messages = []
        async def handle_dialog(dialog):
            dialog_messages.append(dialog.message)
            await dialog.accept()
        frame.on("dialog", handle_dialog)

        # Upload the PDF 'test_documents/sample.pdf' using the file input
        print("[*] Uploading test_documents/sample.pdf...")
        await frame.locator('#pdf-upload').set_input_files('test_documents/sample.pdf')
        await asyncio.sleep(1)
        
        print("[*] Clicking Upload button...")
        await frame.locator('#btn-upload').click(force=True)
        await asyncio.sleep(3) # wait for upload
        
        print("[*] Clicking Reingest button...")
        await frame.locator('#btn-reingest').click(force=True)
        await asyncio.sleep(3) # wait for ingest trigger
        
        # --> Assertions to verify final state
        print("[*] Verifying assertions...")
        assert await frame.locator("text='Bảng điều khiển quản trị'").is_visible() or await frame.locator("text='Khu vực quản trị'").is_visible(), "The admin dashboard should remain accessible after the knowledge update."
        print("[*] Test case TC005 PASSED successfully!")
        await asyncio.sleep(2)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())