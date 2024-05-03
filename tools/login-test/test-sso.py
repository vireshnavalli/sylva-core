from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pathlib import Path
from colorama import Fore, Style
import time
import os

user=os.getenv('USER_SSO')
password=os.getenv('PASSWORD_SSO')
rancher_url=os.getenv('rancher_url')
vault_url=os.getenv('vault_url')
flux_url=os.getenv('flux_url')
harbor_url=os.getenv('harbor_url')
neuvector_url=os.getenv('neuvector_url')
mgmt_only=os.getenv('ONLY_DEPLOY_MGMT')
workload_name=os.getenv('WORKLOAD_CLUSTER_NAME')
download_file=os.getenv('PWD')

options = FirefoxOptions()
options.set_preference("browser.download.dir", download_file)
options.set_preference("browser.download.folderList", 2)
options.set_preference("browser.download.manager.useWindow", False)
options.add_argument("-headless")

def rancher_sso(endpoint, username, password, workload_name):
  print("--------------------------------")
  print("Checking SSO auth Rancher")
  browser = webdriver.Firefox(options=options)
  url='https://' + endpoint
  browser.get(url)
  time.sleep(15)
  print(browser.current_url)
  print(browser.title)
  browser.implicitly_wait(10)
  delay = 30
  try:
    element_present = EC.presence_of_element_located((By.XPATH, '//button[@class="btn bg-primary"]'))
    WebDriverWait(browser, delay).until(element_present)
  except TimeoutException:
    print ("Cannot access SSO option")
    exit (1)
  browser.find_element(By.XPATH, '//button[@class="btn bg-primary"]').click()
  print("Redirect to SSO")
  try:
    element_present = EC.presence_of_element_located((By.ID,"username"))
    WebDriverWait(browser, delay).until(element_present)
  except TimeoutException:
    print ("Cannot access SSO Sign In page")
    exit (1)
  print(browser.title)
  print(browser.current_url)
  browser.implicitly_wait(10)
  browser.find_element(By.ID,"username").send_keys(username)
  browser.find_element(By.ID,"password").send_keys(password)
  browser.find_element(By.ID,"kc-login").click()
  print(browser.current_url)
  print("Waiting to be redirect towards rancher UI home page")
  try:
    mgmt_present = EC.presence_of_element_located((By.XPATH, '//a[@href="/dashboard/c/local/explorer"]'))
    WebDriverWait(browser, delay).until(mgmt_present)
    mgmt_clickable = EC.element_to_be_clickable((By.XPATH, '//a[@href="/dashboard/c/local/explorer"]'))
    WebDriverWait(browser, delay).until(mgmt_clickable)
  except TimeoutException:
    print ("Cannot access the Rancher UI")
    exit(1)
  print("Redirect to rancher UI home page")
  print(browser.current_url)
  if mgmt_only == "TRUE":
      print ("No workload cluster present on this configuration")
      print(Fore.GREEN + "Rancher SSO check done")
      print(Style.RESET_ALL)
      browser.delete_all_cookies()
      browser.quit()
  else:
    cluster=workload_name + '-capi'
    try:
      workload_present = EC.presence_of_element_located((By.LINK_TEXT,cluster))
      WebDriverWait(browser, delay).until(workload_present)
      workload_clickable = EC.element_to_be_clickable((By.LINK_TEXT,cluster))
      WebDriverWait(browser, delay).until(workload_clickable)
    except TimeoutException:
      print ("Cannot access workload cluster in Rancher UI")
      exit(1)
    print ("Switch to workload cluster " + workload_name)
    browser.find_element(By.LINK_TEXT,cluster).click()
    time.sleep(15)
    print(browser.current_url)
    print("Getting kubeconfig for " + workload_name)
    browser.find_elements(By.XPATH, '//button[@class="btn header-btn role-tertiary has-tooltip"]')[2].click()
    rancher_config = workload_name  + '-rancher' + '.yaml'
    file = cluster + '.yaml'
    while not os.path.exists(file):
      print ("Waiting until kubeconfig is successfully downloaded")  
      time.sleep(5)
    os.rename( file, rancher_config)
    print("Check if the kubeconfig has been downloaded")
    path_to_file = rancher_config
    path = Path(path_to_file)
    if path.is_file():
       print(f'The kubeconfig exists')
    else:
      print(f'The kubeconfig does not exist')
    print(Fore.GREEN + "Rancher SSO check done")
    print(Style.RESET_ALL)
    browser.delete_all_cookies()
    browser.quit()

def vault_sso(endpoint, username, password):
  print("--------------------------------")
  print("Checking SSO auth Vault")
  browser = webdriver.Firefox(options=options)
  url='https://' + endpoint
  browser.get(url)
  print(browser.current_url)
  print(browser.title)
  browser.implicitly_wait(10)
  browser.find_element(By.XPATH, '//select[@id="select-ember36"]/option[text()="OIDC"]').click()
  browser.find_element(By.ID,"role").send_keys(username)
  browser.find_element(By.ID,"auth-submit").click()
  browser.find_element(By.XPATH, '//button[@id="auth-submit"]').click()
  browser.implicitly_wait(20)
  time.sleep(25)
  print(browser.current_url)
  windows=browser.window_handles
  vault=windows[0]
  sso=windows[1]
  print("Redirect to SSO")
  delay = 30
  browser.switch_to.window(sso)
  try:
    element_present = EC.presence_of_element_located((By.ID,"username"))
    WebDriverWait(browser, delay).until(element_present)
  except TimeoutException:
    print ("Cannot access SSO Sign In page")
    exit (1)
  print(browser.title)
  print(browser.current_url)
  browser.find_element(By.ID,"username").send_keys(username)
  browser.find_element(By.ID,"password").send_keys(password)
  browser.find_element(By.ID,"kc-login").click()
  print("Waiting to be redirect towards vault UI home page")
  time.sleep(10)
  print("Redirect to vault UI home")
  browser.switch_to.window(vault)
  try:
    element_present = EC.presence_of_element_located((By.ID,"ember70"))
    WebDriverWait(browser, delay).until(element_present)
    print(browser.current_url)
    print(Fore.GREEN + "Vault SSO check done")
    print(Style.RESET_ALL)
  except TimeoutException:
    print ("Cannot access the Vault UI")
    exit(1)
  browser.delete_all_cookies()
  browser.quit()

def flux_sso(endpoint, username, password):
  print("--------------------------------")
  print("Checking SSO auth Flux")
  browser = webdriver.Firefox(options=options)
  url='https://' + endpoint
  browser.get(url)
  print(browser.current_url)
  print(browser.title)
  browser.implicitly_wait(10)
  delay = 40
  try:
    element_present = EC.presence_of_element_located((By.XPATH, '//span[@class="MuiButton-label"]'))
    WebDriverWait(browser, delay).until(element_present)
  except TimeoutException:
    print ("Cannot access SSO option")
    exit (1)
  # force to retry
  retry = 0
  while (retry < 25):
    try:
      browser.find_element(By.XPATH, '//span[@class="MuiButton-label"]').click()
      if browser.title == "Sign in to Sylva":
        break
      retry += 1
    except:
       browser.get(url)
  print("Redirect to SSO")
  try:
    element_present = EC.presence_of_element_located((By.ID,"username"))
    WebDriverWait(browser, delay).until(element_present)
  except TimeoutException:
    print ("Cannot access SSO Sign In page")
    exit (1)
  print(browser.title)
  print(browser.current_url)
  browser.find_element(By.ID,"username").send_keys(username)
  browser.find_element(By.ID,"password").send_keys(password)
  browser.find_element(By.ID,"kc-login").click()
  print(browser.current_url)
  print("Waiting to be redirect towards flux UI home page")
  time.sleep(25)
  print("Redirect to flux UI home page")
  try:
    element_present = EC.presence_of_element_located((By.XPATH, '//a[@href="/applications"]'))
    WebDriverWait(browser, delay).until(element_present)
    print(browser.current_url)
    print(Fore.GREEN + "Flux SSO check done")
    print(Style.RESET_ALL)
  except TimeoutException:
    print ("Cannot access the Flux UI")
    exit(1)
  browser.delete_all_cookies()
  browser.quit()

def neuvector_sso(endpoint, username, password):
   if not endpoint:
      print ("Neuvector is not defined in this configuration")
   else:
      print("--------------------------------")
      browser = webdriver.Firefox(options=options)
      url='https://' + endpoint
      browser.get(url)
      print(browser.current_url)
      print(browser.title)
      time.sleep(40)
      browser.implicitly_wait(10)
      delay = 30 # seconds
      try:
        print("Agree to the End User License Agreement on first login")
        element_present = EC.presence_of_element_located((By.XPATH, '//mat-checkbox[@id="mat-checkbox-1"]'))
        WebDriverWait(browser, delay).until(element_present)
        browser.find_element(By.XPATH, '//mat-checkbox[@id="mat-checkbox-1"]').click()
      except TimeoutException:
         print ("Not first login continue to SSO")
      try:
        element_present = EC.presence_of_element_located((By.XPATH, '//button[normalize-space()="Login with OpenID"]'))
        WebDriverWait(browser, delay).until(element_present)
      except TimeoutException:
        print ("Cannot access SSO option")
        exit (1)
      browser.find_element(By.XPATH, '//button[normalize-space()="Login with OpenID"]').click()
      print("Redirect to SSO")
      try:
        element_present = EC.presence_of_element_located((By.ID,"username"))
        WebDriverWait(browser, delay).until(element_present)
      except TimeoutException:
        print ("Cannot access SSO Sign In page")
        exit (1)
      print(browser.title)
      print(browser.current_url)
      browser.find_element(By.ID,"username").send_keys(username)
      browser.find_element(By.ID,"password").send_keys(password)
      browser.find_element(By.ID,"kc-login").click()
      print("Waiting to be redirect toward neuvector UI home page")
      time.sleep(50)
      print("Redirected to neuvector home page")
      delay = 25 # seconds
      try:
        element_present = EC.presence_of_element_located((By.XPATH, '//a[@href="#/dashboard"]'))
        WebDriverWait(browser, delay).until(element_present)
        print(browser.current_url)
        print(Fore.GREEN + "Neuvector SSO check done")
        print(Style.RESET_ALL)
      except TimeoutException:
        print ("Cannot access the Neuvector UI")
        exit(1)
        browser.delete_all_cookies()
        browser.quit()

def harbor_sso(endpoint, username, password):
  if not endpoint:
      print ("Harbor is not defined in this configuration")
  else:
     print("--------------------------------")
     print("Checking SSO auth Harbor")
     browser = webdriver.Firefox(options=options)
     url='https://' + endpoint
     browser.get(url)
     print(browser.current_url)
     print(browser.title)
     browser.implicitly_wait(10)
     delay = 30
     try:
       element_present = EC.presence_of_element_located((By.XPATH, '//button[@id="log_oidc"]'))
       WebDriverWait(browser, delay).until(element_present)
     except TimeoutException:
       print ("Cannot access SSO option")
       exit (1)
     browser.find_element(By.XPATH, '//button[@id="log_oidc"]').click()
     print("Redirect to SSO")
     try:
       element_present = EC.presence_of_element_located((By.ID,"username"))
       WebDriverWait(browser, delay).until(element_present)
     except TimeoutException:
       print ("Cannot access SSO Sign In page")
       exit (1)
     print(browser.title)
     print(browser.current_url)
     browser.find_element(By.ID,"username").send_keys(username)
     browser.find_element(By.ID,"password").send_keys(password)
     browser.find_element(By.ID,"kc-login").click()
     print(browser.current_url)
     print("Waiting to be redirect towards harbor UI home page")
     time.sleep(25)
     print("Redirect to harbor UI home page")
     try:
       element_present = EC.presence_of_element_located((By.XPATH, '//a[@href="/harbor/registries"]'))
       WebDriverWait(browser, delay).until(element_present)
       print(browser.current_url)
       print(Fore.GREEN + "Harbor SSO check done")
       print(Style.RESET_ALL)
     except TimeoutException:
       print ("Cannot access the Harbor UI")
       exit(1)
     browser.delete_all_cookies()
     browser.quit()

rancher_sso( rancher_url, user, password, workload_name )
vault_sso( vault_url, user, password )
flux_sso( flux_url, user, password )
harbor_sso( harbor_url, user, password )
neuvector_sso( neuvector_url, user, password )
