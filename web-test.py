from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import getpass

# INITIALIZE VARIABLES

delay = 0
time_left = 60

# COLLECT SFDC USERNAME/PASSWORD/SFDC_LIST

print('Input SFDC email address:')
sfdc_username_input = input()
print('SFDC email address has been saved as ' + sfdc_username_input)
password = getpass.getpass()
print('Please enter the direct URL of the SFDC list you would like to work with.')
print('WARNING: You must enter an SFDC classic list - NOT Lightning')
sfdc_target_list = input()
print('Initializing webdriver and logging into SFDC. Please expect a notification from Okta shortly.')





# INITIALIZE BROWSER DRIVER

def launchBrowser():
	chrome_options = Options()
	chrome_options.binary_location="../Google Chrome"
	chrome_options.add_argument("start-maximized");
	driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

	driver.get(sfdc_target_list)

	driver.title #=> "Google"

	driver.implicitly_wait(5)
	return driver

driver = launchBrowser()
print('Webdriver launched')

#OKTA VERIFICATION 

okta_button = driver.find_element(By.XPATH, '//button[@class="button mb24 secondary wide"]')
okta_button.click()

okta_username = driver.find_element(By.NAME, 'username')
okta_password_field = driver.find_element(By.NAME, 'password')
okta_login_button = driver.find_element(By.ID, 'okta-signin-submit')

okta_username.send_keys(sfdc_username_input)
okta_password_field.send_keys(password)
okta_login_button.click()

okta_push_button = driver.find_element(By.XPATH, '//*[@value="Send Push"]')
okta_push_button.click()

print('Okta notification sent. Press any key to continue...')
skip = input()





# CONTACT TRANSFERS #

# LOOP THROUGH ALL CONTACTS AND CREATE A LIST WITH THE NAMES OF EACH CONTACT

print('Opening all contacts in the list in a new tab')
sfdc_contacts_grid = driver.find_elements(By.XPATH, '//div[@class="x-grid3-cell-inner x-grid3-col-FULL_NAME"]')

contacts = []
for contact in sfdc_contacts_grid:
	contacts.append(contact.text)
	print('Adding ' + str(contact.text) + ' to list.')
print('Done verifying contact names..opening contacts')

# OPEN EACH CONTACT IN A NEW TAB

for i in contacts:
	contact_name_link = driver.find_element(By.XPATH, '//a[normalize-space()="' + i + '"]')
	print('Opening ' + i)
	ActionChains(driver).move_to_element(contact_name_link).key_down(Keys.COMMAND).click(contact_name_link).key_up(Keys.COMMAND).perform()
	time.sleep(2)

print('Done opening contacts.. pausing for pageload')
time.sleep(10) 




# SWITCH TO NEXT WINDOW AND GRAB THE MATCHED ACCOUNT SDR, IF NONE GRAB THE MATCHED ACCOUNT AE 
windows = driver.window_handles
driver.switch_to.window(windows[1])

def closeTab():
	driver.find_element(By.ID, 'AppBodyHeader').send_keys(Keys.COMMAND + 'w') 

var = 1
actions_taken = []

for window in windows:
	try:

		driver.switch_to.window(windows[var])

		time.sleep(5)
		close_sfdc_bullshit = driver.find_element(By.ID, 'tryLexDialogX')
		close_sfdc_bullshit.click()
			
		matched_account_sdr = driver.find_element(By.XPATH, '//div[@id="00N6100000IJnrJ_ileinner"]').text
		matched_account_ae = driver.find_element(By.XPATH, '//div[@id="00N6100000IRSgp_ileinner"]').text

		print('Matched account SDR is: ' + matched_account_sdr)
		print('Matched Account Executive is: ' + matched_account_ae)

		change_owner = driver.find_element(By.XPATH, '//a[normalize-space()="[Change]"]')
		change_owner.click()
		time.sleep(3)

		change_owner_input = driver.find_element(By.XPATH, '//input[@id="newOwn"]')
		change_owner_confirm = driver.find_element(By.XPATH, "//input[@title='Save']")
		
		if matched_account_sdr != '':

			# TRANSFER CONTACT TO THE SDR
			change_owner_input.send_keys(matched_account_sdr)
			change_owner_confirm.click()
			
			# TODO - ERROR HANDLING/VALIDATION:

			actions_taken.append('ACTION: TRANSFER CONTACT TO SDR | ' + 'SDR: ' + matched_account_sdr + ' | STATUS: SUCCESS')
			

			time.sleep(5)
			var = var + 1
			driver.close()
			continue

		elif matched_account_ae != '':

			# TRANSFER CONTACT TO THE AE
			change_owner_input.send_keys(matched_account_ae)
			change_owner_confirm.click()

			# TODO - ERROR HANDLING/VALIDATION:

			actions_taken.append('ACTION: TRANSFER CONTACT TO AE | ' + 'AE: ' + matched_account_ae + ' | STATUS: SUCCESS')

			time.sleep(5)
			var = var + 1
			driver.close()

			continue
		else:
			print('This contact does not have an SDR or AE')
			var = var + 1
			driver.close()
			continue
	except IndexError:
		print('All contacts have been transferred.')

		print('The following actions were performed:')
		for i in actions_taken:
			print(actions_taken[i])


