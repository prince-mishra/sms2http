
function Initialize() {
 
  try {
 
    var triggers = ScriptApp.getProjectTriggers();
 
    for (var i in triggers)
      ScriptApp.deleteTrigger(triggers[i]);
 
    ScriptApp.newTrigger("PostFormData")
      .forSpreadsheet(SpreadsheetApp.getActiveSpreadsheet())
      .onFormSubmit().create();
 
  } catch (error) {
    throw new Error("Please add this code in the Google Spreadsheet");
  }
}
 
function PostFormData(e) {
 
  if (!e) {
    throw new Error("Please go the Run menu and choose Initialize");
  }
 
  try {
    var key, entry,
        message = "",
        ss = SpreadsheetApp.getActiveSheet(),
        cols = ss.getRange(1, 1, 1, ss.getLastColumn()).getValues()[0],
        data = {};
    //     lastRow = ss.getRange(ss.getLastRow(), 1, 1,ss.getLastColumn() ).getValues();
    // Logger.log(lastRow);

    for (var keys in cols) {
        key = cols[keys];
      data[key] = e.namedValues[key];
    }
    payload = JSON.stringify(data),
    headers = {};
     var options = { 
        "method":"POST",
        "contentType" : "application/json",
        "headers": headers,
        "payload" : payload
      };
    var response = UrlFetchApp.fetch("<signup_url_here>", options);

  } catch (error) {
    Logger.log(error.toString());
  }
}