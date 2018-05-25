function validateBilling() {
    var x = document.forms["form"]["email"].value;
    var atpos = x.indexOf("@");
    var dotpos = x.lastIndexOf(".");
    if (atpos<1 || dotpos<atpos+2 || dotpos+2>=x.length) {
        alert("Entered E-mail is Not a valid E-mail address");
        return false;
    }
    var len= document.forms["form"]["ccn"].value;
if(len.length<16) {
alert("Credit Card Number must be of 16 digits.");
return false;
}

}
