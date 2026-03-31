from playwright.sync_api import sync_playwright

def run_cuj(page):
    # Wait for the frontend to be ready
    page.goto("http://localhost:3000")
    page.wait_for_timeout(2000)

    # Click on the DI Calculator button
    page.get_by_role("button", name="DI Calculator").click()
    page.wait_for_timeout(1000)

    # Fill in some scores
    try:
        page.locator('input[type="number"]').nth(0).fill('4')
        page.wait_for_timeout(500)
        page.locator('input[type="number"]').nth(1).fill('5')
        page.wait_for_timeout(500)
        page.locator('input[type="number"]').nth(2).fill('3')
        page.wait_for_timeout(500)
    except Exception as e:
        print("Could not fill inputs:", e)

    # Click calculate
    try:
        page.get_by_role("button", name="Calculate DI").click()
        page.wait_for_timeout(2000)
    except Exception as e:
        print("Could not click calculate button:", e)

    # Take screenshot at the key moment
    page.screenshot(path="/home/jules/verification/screenshots/verification.png")
    page.wait_for_timeout(1000)

if __name__ == "__main__":
    import os
    os.makedirs("/home/jules/verification/videos", exist_ok=True)
    os.makedirs("/home/jules/verification/screenshots", exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            record_video_dir="/home/jules/verification/videos"
        )
        page = context.new_page()
        try:
            run_cuj(page)
        finally:
            context.close()
            browser.close()
