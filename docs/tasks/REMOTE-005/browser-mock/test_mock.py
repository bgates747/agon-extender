"""Local synthetic UI checks. Run against the static preview, never a device."""
import json
from playwright.sync_api import sync_playwright

def check():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width":1280,"height":1050})
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8765')
        page.locator('summary').click()
        page.get_by_role('button',name='▸ stress',exact=True).click()
        assert page.locator('#listing tr').count()==129
        page.locator('#all').click()
        assert page.locator('#selection').inner_text()=='129 selected'
        page.locator('#all').click()
        assert page.locator('#selection').inner_text()=='0 selected'
        page.locator('#filter').fill('asset-00')
        page.locator('#all').click()
        assert page.locator('#selection').inner_text()=='9 selected'
        page.locator('#download').click()
        assert page.locator('#queue-list li').count()==9
        page.wait_for_timeout(180)
        page.locator('#cancel').click()
        assert 'cancelled' in page.locator('#queue-summary').inner_text()
        page.locator('#retry').click()
        page.locator('#service').select_option('offline')
        page.wait_for_timeout(200)
        before=page.locator('#overall').get_attribute('value')
        page.wait_for_timeout(250)
        assert page.locator('#overall').get_attribute('value')==before
        assert page.locator('#download').is_disabled()
        page.locator('#service').select_option('busy')
        page.wait_for_timeout(180)
        assert page.locator('#overall').get_attribute('value')==before
        page.locator('#reset').click()
        page.get_by_role('checkbox',name='Select stress',exact=True).check()
        page.locator('#download').click()
        assert page.locator('#queue-list li').count()==130 # root + empty +128
        assert 'empty-folder' in page.locator('#queue-list').inner_text()
        page.locator('#cancel').click()
        page.locator('#reset').click()
        page.get_by_role('checkbox',name='Select autoexec.txt',exact=True).check()
        page.locator('#fail').click()
        page.locator('#download').click()
        page.wait_for_timeout(220)
        assert 'failed' in page.locator('#queue-summary').inner_text()
        page.locator('#retry').click()
        page.wait_for_timeout(700)
        assert '1/1 complete' in page.locator('#queue-summary').inner_text()
        page.locator('#files').set_input_files([{'name':'test.bin','mimeType':'application/octet-stream','buffer':b'abc'}])
        assert page.locator('#queue-list li').count()==2
        page.wait_for_timeout(700)
        page.locator('#mkdir').click()
        page.locator('#new-name').fill('<test>')
        page.locator('#create-folder').click()
        assert page.get_by_role('button',name='▸ <test>',exact=True).count()==1
        assert not errors, errors
        page.screenshot(path='agents/remote005-browser-mock/desktop.png',full_page=True)
        page.set_viewport_size({'width':390,'height':844})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path='agents/remote005-browser-mock/mobile.png',full_page=True)
        print(json.dumps({'result':'pass','browser':browser.version,'checks':['129-entry listing','filtered select/deselect','recursive queue and empty directory','cancel/retry','offline/busy pause','failure/retry','synthetic upload metadata','safe filename text','mobile width','no JS errors']}))
        browser.close()
if __name__=='__main__': check()
