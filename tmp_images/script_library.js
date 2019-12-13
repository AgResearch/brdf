//create a pop-up window

function popup(url,wname,wide,high,scroll)
         {
           if (url != "X") 
           {
             self.name = "main"; // names current window as "main"
             pop_window=window.open(url,wname,'toolbar=0,location=0,directories=0,status=0,menubar=0,scrollbars='+scroll+',resizable=1,width='+wide+',height='+high+'');
             var bname=navigator.appName;
             var bver=parseInt(navigator.appVersion);
             if ((bname == "Microsoft Internet Explorer" && bver >= 4) || (bname == "Netscape" && bver >= 3))
             {
                  pop_window.focus();
             }
           }
}

// check on delete

function ConfirmDelete(){
         if (confirm("Are you sure you want to delete selected item?"))
         {
	    return true;
	 }
	 return false;
}

// enable or disable checkboxes according to dropdown selection

function Enable(form) {
         var i = form.post_type.selectedIndex;
         var length = document.post_form.elements.length;
  
         if (i==2)
         {
             for (var i=0; i<length; i++) 
	     { 
               if (document.post_form.elements[i].name.indexOf("o_notify[]") != -1) 
               document.post_form.elements[i].disabled = false 
             } 
         }
         else
         {
             for (var i=0; i<length; i++) 
	     { 
               if (document.post_form.elements[i].name.indexOf("o_notify[]") != -1) 
               document.post_form.elements[i].disabled = true 
             } 
         }
}

