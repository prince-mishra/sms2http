# sms2http
sms2http is an API for your SMSs. Once the android app is properly configured, it sends all incoming SMS to the configured web endpoint, where they can later be accessed over a json API. 

Before deploying
----------------
 1. Replace sendgrid key in webapp/client/views.py
 2. Replace server FQDN in utils/onFormSubmit.js (assuming you are using it)

Usage
------
 1. Request api_url for your phone_number here -  (google form) 
 2. You will receive api_url in response. 
 3. Install the app on an android device. Download the app here - (releases/*.apk)
 4. Inside the app, go to "Additional Settings" => "sms2http endpoint". Punch the api_url which you received in step 1 above. Save. You're done.
 5. Send SMS to your registered phone number
 6. All SMSs will be visible at api_url. This is a RESTful API. Feel free to get creative
