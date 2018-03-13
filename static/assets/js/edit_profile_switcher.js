function showHiddenField (field)
{
  //Removes the a_ of the string, so the rest of the script can use the Django default html id
  var cleanField = field;
  cleanField = cleanField.replace('a_','');

  var hiddenField = cleanField + "-hidden";
  var valueField = cleanField +"-value";
  var textUpdate = "";

  //Catches Enter press and simulates a click in the pencil "a_element_of_the_form"
  document.body.onkeydown = function(e)
  {
    if (e.keyCode == 13 || e.which == 13)
    {
      document.getElementById(field).click();
      return false;
    };
  };

  //Checks the style in the css of the hiddenField, so it can be switched to view or hidden
  if ( getComputedStyle(document.getElementById(hiddenField),null).getPropertyValue("display") == "none")
  {
    //Hides the valueField, shows the hiddenField
    document.getElementById(valueField).style.display = "none";
    document.getElementById(hiddenField).style.display = "inline-block";
  }
  else
  {
    //Hides the hiddenField and shows the valueField
    document.getElementById(valueField).style.display = "inline-block";
    document.getElementById(hiddenField).style.display = "none";
    //Updates the textUpdate to compare
    textUpdate = document.getElementById(cleanField).value;
    //If the value was from the picklist, it was updated with Lv 2, Lv 4, etc. hence this check.
    if (cleanField == "id_corporate_level" || cleanField == "id_company")
    {
      var e = document.getElementById(cleanField);
      textUpdate = e.options[e.selectedIndex].text;
    };
    //Checks if the user updated something, comparing it to the earlier value
    //Updates the "read-only" text and changes the color
    if (textUpdate != document.getElementById(valueField).textContent)
    {
        document.getElementById(valueField).textContent= textUpdate;
        document.getElementById(valueField).style.color = "black";
    };
  };
};
