function ValidateEmail() {
    var x = document.forms["form"]["email"].value;
    var atpos = x.indexOf("@");
    var dotpos = x.lastIndexOf(".");
    if (atpos<1 || dotpos<atpos+2 || dotpos+2>=x.length) {
        alert("Entered E-mail is Not a valid E-mail address");
        return false;
    }
}